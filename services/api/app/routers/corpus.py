from __future__ import annotations

import re
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.app.core.config import get_settings
from services.api.app.core.db import get_session
from services.api.app.deps import get_vector_store
from services.api.app.domain.enums import IngestionStatus, RightsStatus
from services.api.app.models import Chunk, ChunkReviewEvent, IngestionRun, Source, SourceFile, SourceReviewEvent
from services.api.app.schemas import (
    ChunkOut,
    ChunkReviewDecision,
    ChunkReviewEventOut,
    CorpusDashboardOut,
    CorpusUploadOut,
    RightsDecisionRequest,
    SourceFileOut,
    SourceOut,
    SourcePromotionRequest,
    SourceReviewEventOut,
)
from services.api.app.services.corpus_review import can_promote_source, distribution
from services.api.app.services.hashutil import sha256_bytes, sha256_text
from services.api.app.services.ingestion import ingest_plaintext_source
from services.api.app.services.text_extraction import extract_text_from_bytes

router = APIRouter(prefix="/corpus", tags=["corpus-ingestion-review"])


@router.post("/upload", response_model=CorpusUploadOut, status_code=status.HTTP_201_CREATED)
async def upload_corpus_file(
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    language: str = Form(default="hi"),
    rights_status: str = Form(default="UNKNOWN"),
    tradition_scope: str = Form(default=""),
    source_type: str | None = Form(default=None),
    locator: str | None = Form(default=None),
    session: AsyncSession = Depends(get_session),
) -> CorpusUploadOut:
    settings = get_settings()
    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="uploaded file is empty")
    if len(raw) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail=f"file exceeds max upload bytes: {settings.max_upload_bytes}")
    try:
        rights = RightsStatus(rights_status)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"invalid rights_status: {rights_status}") from exc

    extraction = extract_text_from_bytes(file.filename or "upload.txt", raw, enable_pdf=settings.enable_pdf_extraction)
    if not extraction.text:
        raise HTTPException(status_code=422, detail={"message": "no text extracted", "extraction": extraction.report})

    src = Source(
        source_type=source_type or extraction.source_type,
        title=title or _title_from_filename(file.filename),
        language=language,
        tradition_scope=[x.strip() for x in tradition_scope.split(",") if x.strip()],
        rights_status=rights.value,
        ingestion_status=IngestionStatus.INGESTED.value,
        checksum_sha256=extraction.checksum_sha256,
        source_metadata={"locator": locator, "extraction": extraction.report} if locator else {"extraction": extraction.report},
    )
    session.add(src)
    await session.flush()

    storage_uri = _write_upload(settings.upload_dir, src.id, file.filename or "upload.bin", raw)
    source_file = SourceFile(
        source_id=src.id,
        original_filename=file.filename or "upload.bin",
        content_type=file.content_type,
        byte_size=len(raw),
        checksum_sha256=sha256_bytes(raw),
        storage_uri=storage_uri,
        extraction_status="COMPLETED" if extraction.text else "EMPTY",
        extraction_report=extraction.report,
    )
    session.add(source_file)
    await session.flush()

    report = await ingest_plaintext_source(
        session,
        source=src,
        text=extraction.text,
        vector_store=get_vector_store(),
        embedding_dim=settings.embedding_dim,
    )
    run = IngestionRun(
        source_id=src.id,
        source_file_id=source_file.id,
        status="COMPLETED",
        stage_report={"extraction": extraction.report, "ingestion": report.__dict__},
        chunks_created=report.chunks_created,
        indexed=report.indexed,
    )
    session.add(run)
    await session.commit()
    await session.refresh(src)
    await session.refresh(source_file)
    return CorpusUploadOut(
        source=SourceOut.model_validate(src),
        source_file=SourceFileOut.model_validate(source_file),
        extraction=extraction.report,
        ingestion_report=report.__dict__,
    )


@router.get("/files", response_model=list[SourceFileOut])
async def list_source_files(
    limit: int = Query(default=50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
) -> list[SourceFileOut]:
    result = await session.execute(select(SourceFile).order_by(SourceFile.created_at.desc()).limit(limit))
    return [SourceFileOut.model_validate(row) for row in result.scalars().all()]


@router.get("/review/sources", response_model=list[SourceOut])
async def source_review_queue(
    ingestion_status: str | None = Query(default=None),
    rights_status: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
) -> list[SourceOut]:
    stmt = select(Source).order_by(Source.created_at.desc()).limit(limit)
    if ingestion_status:
        stmt = stmt.where(Source.ingestion_status == ingestion_status)
    if rights_status:
        stmt = stmt.where(Source.rights_status == rights_status)
    result = await session.execute(stmt)
    return [SourceOut.model_validate(row) for row in result.scalars().all()]


@router.post("/sources/{source_id}/rights", response_model=SourceReviewEventOut)
async def decide_rights(
    source_id: str,
    payload: RightsDecisionRequest,
    session: AsyncSession = Depends(get_session),
) -> SourceReviewEventOut:
    source = await session.get(Source, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="source not found")
    source.rights_status = payload.rights_status.value
    source.source_metadata = {**(source.source_metadata or {}), "rights_evidence": payload.evidence}
    event = SourceReviewEvent(
        source_id=source.id,
        reviewer_id=payload.reviewer_id,
        decision="RIGHTS_DECISION",
        rights_status=payload.rights_status.value,
        ingestion_status=source.ingestion_status,
        evidence=payload.evidence,
        notes=payload.notes,
    )
    session.add(event)
    await session.commit()
    await session.refresh(event)
    return SourceReviewEventOut.model_validate(event)


@router.post("/sources/{source_id}/promote", response_model=SourceReviewEventOut)
async def promote_source(
    source_id: str,
    payload: SourcePromotionRequest,
    session: AsyncSession = Depends(get_session),
) -> SourceReviewEventOut:
    settings = get_settings()
    source = await session.get(Source, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="source not found")
    check = can_promote_source(
        target_status=payload.target_status,
        rights_status=source.rights_status,
        require_rights_for_z2=settings.corpus_require_rights_for_z2,
    )
    if not check.allowed:
        raise HTTPException(status_code=409, detail=check.reason)
    source.ingestion_status = payload.target_status
    event = SourceReviewEvent(
        source_id=source.id,
        reviewer_id=payload.reviewer_id,
        decision="PROMOTE_SOURCE",
        rights_status=source.rights_status,
        ingestion_status=payload.target_status,
        evidence=payload.evidence,
        notes=payload.notes,
    )
    session.add(event)
    await session.commit()
    await session.refresh(event)
    return SourceReviewEventOut.model_validate(event)


@router.get("/review/chunks", response_model=list[ChunkOut])
async def chunk_review_queue(
    review_status: str = Query(default="REVIEW_PENDING"),
    source_id: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
) -> list[ChunkOut]:
    stmt = select(Chunk).where(Chunk.review_status == review_status).order_by(Chunk.created_at.desc()).limit(limit)
    if source_id:
        stmt = stmt.where(Chunk.source_id == source_id)
    result = await session.execute(stmt)
    return [ChunkOut.model_validate(row) for row in result.scalars().all()]


@router.patch("/chunks/{chunk_id}/review", response_model=ChunkReviewEventOut)
async def review_chunk(
    chunk_id: str,
    payload: ChunkReviewDecision,
    session: AsyncSession = Depends(get_session),
) -> ChunkReviewEventOut:
    chunk = await session.get(Chunk, chunk_id)
    if chunk is None:
        raise HTTPException(status_code=404, detail="chunk not found")
    previous_status = chunk.review_status
    previous_hash = sha256_text(chunk.chunk_text)
    new_status = _status_from_chunk_decision(payload.decision)
    if payload.revised_text is not None:
        chunk.chunk_text = payload.revised_text.strip()
        chunk.token_count = len(chunk.chunk_text.split())
    if payload.quality_score is not None:
        chunk.quality_score = payload.quality_score
    chunk.review_status = new_status
    event = ChunkReviewEvent(
        chunk_id=chunk.id,
        reviewer_id=payload.reviewer_id,
        decision=payload.decision,
        previous_status=previous_status,
        new_status=new_status,
        previous_text_hash=previous_hash,
        revised_text_hash=sha256_text(chunk.chunk_text),
        checklist=payload.checklist,
        notes=payload.notes,
    )
    session.add(event)
    await session.commit()
    await session.refresh(event)
    return ChunkReviewEventOut.model_validate(event)


@router.get("/dashboard", response_model=CorpusDashboardOut)
async def corpus_dashboard(session: AsyncSession = Depends(get_session)) -> CorpusDashboardOut:
    sources = list((await session.execute(select(Source))).scalars().all())
    files = list((await session.execute(select(SourceFile))).scalars().all())
    chunks = list((await session.execute(select(Chunk))).scalars().all())
    return CorpusDashboardOut(
        sources_total=len(sources),
        files_total=len(files),
        chunks_total=len(chunks),
        pending_source_reviews=sum(1 for s in sources if s.rights_status == "UNKNOWN" or s.ingestion_status in {"INGESTED", "PARSED", "CHUNKED", "EMBEDDED", "INDEXED"}),
        pending_chunk_reviews=sum(1 for c in chunks if c.review_status == "REVIEW_PENDING"),
        approved_z2_sources=sum(1 for s in sources if s.ingestion_status == "APPROVED_Z2"),
        indexed_sources=sum(1 for s in sources if s.ingestion_status == "INDEXED"),
        rights_distribution=distribution(s.rights_status for s in sources),
        ingestion_distribution=distribution(s.ingestion_status for s in sources),
    )


def _write_upload(upload_dir: str, source_id: str, filename: str, raw: bytes) -> str:
    safe = _safe_filename(filename)
    digest = sha256_bytes(raw)[:16]
    directory = Path(upload_dir) / source_id
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{digest}_{safe}"
    path.write_bytes(raw)
    return str(path)


def _safe_filename(filename: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", filename).strip("._")
    return cleaned or "upload.bin"


def _title_from_filename(filename: str | None) -> str:
    if not filename:
        return "Untitled Source"
    return Path(filename).stem.replace("_", " ").replace("-", " ").strip() or filename


def _status_from_chunk_decision(decision: str) -> str:
    return {
        "approve": "APPROVED",
        "reject": "REJECTED",
        "needs_revision": "NEEDS_REVISION",
        "revise": "REVIEW_PENDING",
        "deprecate": "DEPRECATED",
    }[decision]
