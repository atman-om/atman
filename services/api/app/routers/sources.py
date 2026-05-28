from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.app.core.config import get_settings
from services.api.app.core.db import get_session
from services.api.app.deps import get_vector_store
from services.api.app.domain.enums import IngestionStatus, RightsStatus
from services.api.app.models import Source
from services.api.app.schemas import SourceCreate, SourceDecision, SourceOut, ChunkOut
from services.api.app.services.ingestion import ingest_plaintext_source

router = APIRouter(prefix="/sources", tags=["sources"])


@router.post("", response_model=SourceOut)
async def create_source(payload: SourceCreate, session: AsyncSession = Depends(get_session)) -> SourceOut:
    source = Source(
        source_type=payload.source_type,
        title=payload.title,
        language=payload.language,
        tradition_scope=payload.tradition_scope,
        rights_status=payload.rights_status.value,
        ingestion_status=IngestionStatus.INGESTED.value,
        source_metadata=payload.source_metadata,
    )
    session.add(source)
    await session.commit()
    await session.refresh(source)
    if payload.text:
        settings = get_settings()
        await ingest_plaintext_source(
            session,
            source=source,
            text=payload.text,
            vector_store=get_vector_store(),
            embedding_dim=settings.embedding_dim,
        )
        await session.refresh(source)
    return SourceOut.model_validate(source)


@router.get("", response_model=list[SourceOut])
async def list_sources(
    limit: int = Query(default=50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
) -> list[SourceOut]:
    result = await session.execute(select(Source).order_by(Source.created_at.desc()).limit(limit))
    return [SourceOut.model_validate(row) for row in result.scalars().all()]


@router.get("/{source_id}", response_model=SourceOut)
async def get_source(source_id: str, session: AsyncSession = Depends(get_session)) -> SourceOut:
    source = await session.get(Source, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="source not found")
    return SourceOut.model_validate(source)


@router.post("/{source_id}/decision", response_model=SourceOut)
async def decide_source(
    source_id: str,
    payload: SourceDecision,
    session: AsyncSession = Depends(get_session),
) -> SourceOut:
    source = await session.get(Source, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="source not found")
    if payload.decision == "reject":
        source.ingestion_status = IngestionStatus.BLOCKED.value
        source.rights_status = RightsStatus.REJECTED.value
    elif payload.decision == "needs_cleanup":
        source.ingestion_status = IngestionStatus.REVIEW_PENDING.value
    elif payload.decision == "promote_z0_to_z1":
        source.ingestion_status = IngestionStatus.APPROVED_Z1.value
    elif payload.decision == "promote_z1_to_z2":
        if source.rights_status in {RightsStatus.UNKNOWN.value, RightsStatus.REJECTED.value, RightsStatus.NO_STORAGE_ALLOWED.value}:
            raise HTTPException(status_code=409, detail="source rights do not allow Z2 promotion")
        source.ingestion_status = IngestionStatus.APPROVED_Z2.value
    elif payload.decision == "mark_reference_only":
        source.rights_status = RightsStatus.REFERENCE_ONLY.value
    elif payload.decision == "mark_rights_red":
        source.rights_status = RightsStatus.REJECTED.value
        source.ingestion_status = IngestionStatus.BLOCKED.value
    source.source_metadata = {**(source.source_metadata or {}), "last_decision": payload.model_dump()}
    await session.commit()
    await session.refresh(source)
    return SourceOut.model_validate(source)


@router.get("/{source_id}/chunks", response_model=list[ChunkOut])
async def list_chunks(source_id: str, session: AsyncSession = Depends(get_session)) -> list[ChunkOut]:
    source = await session.get(Source, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="source not found")
    from services.api.app.models import Chunk
    result = await session.execute(select(Chunk).where(Chunk.source_id == source_id).order_by(Chunk.chunk_order))
    return [ChunkOut.model_validate(row) for row in result.scalars().all()]
