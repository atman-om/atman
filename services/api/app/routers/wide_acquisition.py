from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.app.core.db import get_session
from services.api.app.models import AcquisitionJob, ProductEvent, SourceSnapshot
from services.api.app.schemas import AcquisitionJobCreate, AcquisitionJobOut
from services.api.app.services.hashutil import sha256_text
from services.api.app.services.wide_acquisition import assess_acquisition_candidate

router = APIRouter(prefix="/acquisition", tags=["wide-acquisition-v1.0.5"])


@router.post("/jobs", response_model=AcquisitionJobOut)
async def create_job(payload: AcquisitionJobCreate, session: AsyncSession = Depends(get_session)) -> AcquisitionJobOut:
    assessment = assess_acquisition_candidate(
        uri=payload.source_uri,
        text=payload.extracted_text,
        rights_signal=payload.rights_signal,
        mode=payload.mode,
    )
    row = AcquisitionJob(
        source_uri=payload.source_uri,
        mode=payload.mode,
        status=assessment.status,
        zone=assessment.zone,
        discovered_title=payload.discovered_title,
        quality_score=assessment.quality_score,
        rights_signal=payload.rights_signal,
        canonical_candidate=payload.canonical_candidate,
        report=assessment.report,
    )
    session.add(row)
    if payload.extracted_text:
        session.add(SourceSnapshot(
            source_uri=payload.source_uri,
            source_kind="web_or_book",
            zone=assessment.zone,
            title=payload.discovered_title,
            content_hash=sha256_text(payload.extracted_text),
            extracted_text_preview=payload.extracted_text[:2000],
            rights_observation=payload.rights_signal,
            quality_score=assessment.quality_score,
            metadata={"acquisition_mode": payload.mode, "job_report": assessment.report},
        ))
    await session.flush()
    session.add(ProductEvent(event_type="acquisition_job_created", object_type="acquisition_job", object_id=row.id, event_metadata={"zone": row.zone, "quality_score": row.quality_score}))
    await session.commit()
    await session.refresh(row)
    return AcquisitionJobOut.model_validate(row)


@router.get("/jobs", response_model=list[AcquisitionJobOut])
async def list_jobs(
    zone: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
) -> list[AcquisitionJobOut]:
    stmt = select(AcquisitionJob).order_by(AcquisitionJob.created_at.desc()).limit(limit)
    if zone:
        stmt = select(AcquisitionJob).where(AcquisitionJob.zone == zone).order_by(AcquisitionJob.created_at.desc()).limit(limit)
    result = await session.execute(stmt)
    return [AcquisitionJobOut.model_validate(row) for row in result.scalars().all()]
