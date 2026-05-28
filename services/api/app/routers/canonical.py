from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.app.core.config import get_settings
from services.api.app.core.db import get_session
from services.api.app.models import CanonicalPassage, CanonicalWork, ClaimEvidence, CorpusPromotionEvent, SourceSnapshot
from services.api.app.services.canonical_corpus import (
    build_internal_evidence_record,
    locator_sort_key,
    normalize_locator,
    render_citations,
    score_claim_against_text,
    source_authority_score,
    summarize_manifest_counts,
    text_hash,
    zone_transition_allowed,
)

router = APIRouter(prefix="/canonical", tags=["canonical-corpus-v1.0.1"])

CitationMode = Literal["hidden", "source", "scholar"]


class CanonicalWorkCreate(BaseModel):
    work_key: str = Field(min_length=2, max_length=128)
    title_sa: str | None = None
    title_hi: str | None = None
    title_en: str | None = None
    category: str = Field(min_length=2, max_length=128)
    tradition_scope: list[str] = Field(default_factory=list)
    authority_level: str = "PRIMARY"
    canonical_status: str = "DRAFT"
    metadata: dict[str, Any] = Field(default_factory=dict)


class CanonicalWorkOut(CanonicalWorkCreate):
    id: str
    metadata: dict[str, Any] = Field(default_factory=dict, validation_alias="metadata_json", serialization_alias="metadata")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class CanonicalPassageCreate(BaseModel):
    work_id: str
    edition_id: str | None = None
    locator: str = Field(min_length=1, max_length=256)
    sanskrit_text: str | None = None
    normalized_text: str = Field(min_length=1)
    translation_hi: str | None = None
    translation_en: str | None = None
    chapter: str | None = None
    verse: str | None = None
    section: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.75, ge=0.0, le=1.0)
    review_status: str = "CANDIDATE"
    metadata: dict[str, Any] = Field(default_factory=dict)


class CanonicalPassageOut(BaseModel):
    id: str
    work_id: str
    edition_id: str | None
    locator: str
    sanskrit_text: str | None
    normalized_text: str
    translation_hi: str | None
    translation_en: str | None
    chapter: str | None
    verse: str | None
    section: str | None
    source_ids: list[str]
    confidence: float
    review_status: str
    authority_score: float
    metadata: dict[str, Any] = Field(default_factory=dict, validation_alias="metadata_json", serialization_alias="metadata")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class SourceSnapshotCreate(BaseModel):
    source_uri: str = Field(min_length=2, max_length=2048)
    source_kind: str = "web"
    zone: str = "Z1_QUARANTINE"
    title: str | None = None
    extracted_text: str = Field(default="", description="Raw text is stored externally in production; API stores preview/hash.")
    raw_text_uri: str | None = None
    robots_status: str = "UNKNOWN"
    rights_observation: str = "UNKNOWN"
    quality_score: float = Field(default=0.0, ge=0.0, le=1.0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SourceSnapshotOut(BaseModel):
    id: str
    source_uri: str
    source_kind: str
    zone: str
    title: str | None
    content_hash: str
    extracted_text_preview: str | None
    robots_status: str
    rights_observation: str
    quality_score: float
    metadata: dict[str, Any] = Field(default_factory=dict, validation_alias="metadata_json", serialization_alias="metadata")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ClaimCheckRequest(BaseModel):
    claim: str = Field(min_length=2, max_length=4000)
    top_k: int = Field(default=5, ge=1, le=25)
    min_score: float | None = Field(default=None, ge=0.0, le=1.0)


class ClaimCheckResponse(BaseModel):
    claim: str
    passed: bool
    best_grade: str
    evidence: list[dict[str, Any]]
    internal_evidence_required: bool = True


class AnswerGenerateRequest(BaseModel):
    question: str = Field(min_length=2, max_length=4000)
    language: str = "hi"
    citation_mode: CitationMode = "hidden"
    top_k: int = Field(default=5, ge=1, le=20)


class AnswerGenerateResponse(BaseModel):
    answer: str
    citation_mode: CitationMode
    visible_citations: list[dict[str, Any]]
    internal_evidence: list[dict[str, Any]]
    confidence: str


class PromotionRequest(BaseModel):
    object_type: Literal["source_snapshot", "canonical_passage", "canonical_work"]
    object_id: str
    from_zone: str
    to_zone: str
    decision: str = "promote"
    reviewer_id: str | None = None
    evidence: dict[str, Any] = Field(default_factory=dict)


@router.post("/works", response_model=CanonicalWorkOut)
async def create_work(payload: CanonicalWorkCreate, session: AsyncSession = Depends(get_session)) -> CanonicalWorkOut:
    row = CanonicalWork(**payload.model_dump(exclude={"metadata"}), metadata_json=payload.metadata)
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return CanonicalWorkOut.model_validate(row)


@router.get("/works", response_model=list[CanonicalWorkOut])
async def list_works(
    q: str | None = None,
    category: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
) -> list[CanonicalWorkOut]:
    stmt = select(CanonicalWork)
    if q:
        stmt = stmt.where(or_(CanonicalWork.work_key.icontains(q), CanonicalWork.title_hi.icontains(q), CanonicalWork.title_en.icontains(q)))
    if category:
        stmt = stmt.where(CanonicalWork.category == category)
    stmt = stmt.order_by(CanonicalWork.category.asc(), CanonicalWork.work_key.asc()).limit(limit)
    result = await session.execute(stmt)
    return [CanonicalWorkOut.model_validate(row) for row in result.scalars().all()]


@router.post("/passages", response_model=CanonicalPassageOut)
async def create_passage(payload: CanonicalPassageCreate, session: AsyncSession = Depends(get_session)) -> CanonicalPassageOut:
    work = await session.get(CanonicalWork, payload.work_id)
    if work is None:
        raise HTTPException(status_code=404, detail="canonical work not found")
    locator = normalize_locator(payload.locator)
    row = CanonicalPassage(
        **(payload.model_dump(exclude={"locator"})),
        locator=locator,
        locator_sort_key=locator_sort_key(locator),
        authority_score=source_authority_score(work.authority_level, payload.review_status, payload.confidence),
        metadata_json=payload.metadata,
    )
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return CanonicalPassageOut.model_validate(row)


@router.get("/passages/search", response_model=list[CanonicalPassageOut])
async def search_passages(
    q: str,
    work_id: str | None = None,
    limit: int = Query(default=25, ge=1, le=250),
    session: AsyncSession = Depends(get_session),
) -> list[CanonicalPassageOut]:
    stmt = select(CanonicalPassage).where(
        or_(
            CanonicalPassage.locator.icontains(q),
            CanonicalPassage.normalized_text.icontains(q),
            CanonicalPassage.translation_hi.icontains(q),
            CanonicalPassage.translation_en.icontains(q),
        )
    )
    if work_id:
        stmt = stmt.where(CanonicalPassage.work_id == work_id)
    stmt = stmt.order_by(CanonicalPassage.authority_score.desc(), CanonicalPassage.locator_sort_key.asc()).limit(limit)
    result = await session.execute(stmt)
    return [CanonicalPassageOut.model_validate(row) for row in result.scalars().all()]


@router.post("/source-snapshots", response_model=SourceSnapshotOut)
async def create_source_snapshot(payload: SourceSnapshotCreate, session: AsyncSession = Depends(get_session)) -> SourceSnapshotOut:
    text = payload.extracted_text or ""
    row = SourceSnapshot(
        source_uri=payload.source_uri,
        source_kind=payload.source_kind,
        zone=payload.zone,
        title=payload.title,
        content_hash=text_hash(text),
        raw_text_uri=payload.raw_text_uri,
        extracted_text_preview=text[:2000],
        robots_status=payload.robots_status,
        rights_observation=payload.rights_observation,
        quality_score=payload.quality_score,
        metadata_json=payload.metadata,
    )
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return SourceSnapshotOut.model_validate(row)


@router.post("/import/manifest")
async def import_manifest(manifest: dict[str, Any], session: AsyncSession = Depends(get_session)) -> dict[str, Any]:
    settings = get_settings()
    counts = summarize_manifest_counts(manifest)
    if counts["passages"] > settings.canonical_bulk_import_max_passages:
        raise HTTPException(status_code=413, detail="manifest exceeds ATMAN_CANONICAL_BULK_IMPORT_MAX_PASSAGES")
    work_key_to_id: dict[str, str] = {}
    for work in manifest.get("works", []):
        work_payload = CanonicalWorkCreate(**work)
        row = CanonicalWork(**work_payload.model_dump(exclude={"metadata"}), metadata_json=work_payload.metadata)
        session.add(row)
        await session.flush()
        work_key_to_id[row.work_key] = row.id
    imported_passages = 0
    for passage in manifest.get("passages", []):
        work_id = passage.get("work_id") or work_key_to_id.get(passage.get("work_key"))
        if not work_id:
            continue
        payload = CanonicalPassageCreate(**{k: v for k, v in passage.items() if k != "work_key"} | {"work_id": work_id})
        work = await session.get(CanonicalWork, work_id)
        locator = normalize_locator(payload.locator)
        row = CanonicalPassage(
            **payload.model_dump(exclude={"locator"}),
            locator=locator,
            locator_sort_key=locator_sort_key(locator),
            authority_score=source_authority_score(work.authority_level if work else "PRIMARY", payload.review_status, payload.confidence),
            metadata_json=payload.metadata,
        )
        session.add(row)
        imported_passages += 1
    await session.commit()
    return {"imported": {"works": len(work_key_to_id), "passages": imported_passages}, "manifest_counts": counts}


@router.post("/claims/check", response_model=ClaimCheckResponse)
async def check_claim(payload: ClaimCheckRequest, session: AsyncSession = Depends(get_session)) -> ClaimCheckResponse:
    settings = get_settings()
    threshold = payload.min_score if payload.min_score is not None else settings.canonical_min_claim_support_score
    # Broad deterministic candidate retrieval; production can replace this with vector + graph retrieval.
    terms = [term for term in payload.claim.split() if len(term) > 2][:8]
    stmt = select(CanonicalPassage).limit(payload.top_k)
    if terms:
        stmt = select(CanonicalPassage).where(or_(*[CanonicalPassage.normalized_text.icontains(term) for term in terms])).limit(payload.top_k)
    result = await session.execute(stmt)
    passages = result.scalars().all()
    evidence: list[dict[str, Any]] = []
    for passage in passages:
        support = score_claim_against_text(payload.claim, " ".join(filter(None, [passage.normalized_text, passage.translation_hi, passage.translation_en])), passage.authority_score)
        record = {
            "passage_id": passage.id,
            "locator": passage.locator,
            "support_score": support.support_score,
            "evidence_grade": support.evidence_grade,
            "matched_terms": support.matched_terms,
            "missing_terms": support.missing_terms[:20],
        }
        evidence.append(record)
        session.add(ClaimEvidence(claim_text=payload.claim, passage_id=passage.id, support_score=support.support_score, evidence_grade=support.evidence_grade, report=record))
    await session.commit()
    evidence.sort(key=lambda item: item["support_score"], reverse=True)
    best = evidence[0] if evidence else {"support_score": 0.0, "evidence_grade": "F"}
    return ClaimCheckResponse(claim=payload.claim, passed=best["support_score"] >= threshold, best_grade=best["evidence_grade"], evidence=evidence)


@router.post("/answers/generate", response_model=AnswerGenerateResponse)
async def generate_answer(payload: AnswerGenerateRequest, session: AsyncSession = Depends(get_session)) -> AnswerGenerateResponse:
    settings = get_settings()
    citation_mode = payload.citation_mode or settings.canonical_default_citation_mode
    terms = [term for term in payload.question.split() if len(term) > 2][:8]
    stmt = select(CanonicalPassage).limit(payload.top_k)
    if terms:
        stmt = select(CanonicalPassage).where(or_(*[CanonicalPassage.normalized_text.icontains(term) for term in terms])).limit(payload.top_k)
    result = await session.execute(stmt)
    passages = result.scalars().all()
    evidence: list[dict[str, Any]] = []
    for passage in passages:
        work = await session.get(CanonicalWork, passage.work_id)
        support = score_claim_against_text(payload.question, " ".join(filter(None, [passage.normalized_text, passage.translation_hi, passage.translation_en])), passage.authority_score)
        evidence.append(build_internal_evidence_record(
            passage_id=passage.id,
            work_key=work.work_key if work else "UNKNOWN",
            title_hi=work.title_hi if work else None,
            title_en=work.title_en if work else None,
            locator=passage.locator,
            support=support,
            preview=passage.translation_hi or passage.translation_en or passage.normalized_text,
        ))
    evidence.sort(key=lambda item: item["support_score"], reverse=True)
    if not evidence:
        answer = "इस प्रश्न के लिए अभी canonical corpus में पर्याप्त प्रमाण नहीं मिला। इसे review queue में भेजना चाहिए।"
        confidence = "unsupported"
    else:
        top = evidence[0]
        answer = f"इस प्रश्न पर Atman को canonical corpus में {top['work_key']} {top['locator']} से आंतरिक आधार मिला। सरल उत्तर: उपलब्ध स्रोत के आधार पर उत्तर तैयार किया जा सकता है, पर production में Qwen runtime इसे अधिक स्वाभाविक भाषा में विस्तृत करेगा।"
        confidence = top["evidence_grade"]
    return AnswerGenerateResponse(
        answer=answer,
        citation_mode=citation_mode,  # type: ignore[arg-type]
        visible_citations=render_citations(evidence, citation_mode),
        internal_evidence=evidence,
        confidence=confidence,
    )


@router.post("/promotions")
async def promote_corpus_object(payload: PromotionRequest, session: AsyncSession = Depends(get_session)) -> dict[str, Any]:
    if not zone_transition_allowed(payload.from_zone, payload.to_zone):
        raise HTTPException(status_code=409, detail="zone transition is not allowed")
    row = CorpusPromotionEvent(**payload.model_dump())
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return {"promotion_event_id": row.id, "allowed": True, "to_zone": row.to_zone}
