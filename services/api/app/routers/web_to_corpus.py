from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.app.core.config import get_settings
from services.api.app.core.db import get_session
from services.api.app.models import CrawlJob, ProvenanceEvent
from services.api.app.schemas import (
    ProvenanceEventOut,
    WebCrawlJobOut,
    WebCrawlJobRequest,
    WebQualityScoreRequest,
    WebQualityScoreResponse,
)
from services.api.app.services.web_quality import score_web_source_text
from services.api.app.services.web_to_corpus import create_crawl_job

router = APIRouter(prefix="/web-to-corpus", tags=["web-to-corpus"])


@router.post("/jobs", response_model=WebCrawlJobOut)
async def create_job(payload: WebCrawlJobRequest, session: AsyncSession = Depends(get_session)) -> WebCrawlJobOut:
    row = await create_crawl_job(
        session,
        url=str(payload.url),
        rights_status=payload.rights_status,
        fetch_now=payload.fetch_now,
        force=payload.force,
        settings=get_settings(),
    )
    return WebCrawlJobOut.model_validate(row)


@router.get("/jobs", response_model=list[WebCrawlJobOut])
async def list_jobs(limit: int = Query(default=50, ge=1, le=250), session: AsyncSession = Depends(get_session)) -> list[WebCrawlJobOut]:
    result = await session.execute(select(CrawlJob).order_by(CrawlJob.created_at.desc()).limit(limit))
    return [WebCrawlJobOut.model_validate(row) for row in result.scalars().all()]


@router.get("/jobs/{job_id}", response_model=WebCrawlJobOut)
async def get_job(job_id: str, session: AsyncSession = Depends(get_session)) -> WebCrawlJobOut:
    row = await session.get(CrawlJob, job_id)
    if row is None:
        raise HTTPException(status_code=404, detail="crawl job not found")
    return WebCrawlJobOut.model_validate(row)


@router.post("/quality/score", response_model=WebQualityScoreResponse)
async def score_quality(payload: WebQualityScoreRequest) -> WebQualityScoreResponse:
    result = score_web_source_text(
        payload.text,
        url=str(payload.url),
        rights_status=payload.rights_status.value,
        robots_status=payload.robots_status,
    )
    return WebQualityScoreResponse(**result.__dict__)


@router.get("/provenance/{object_type}/{object_id}", response_model=list[ProvenanceEventOut])
async def provenance_events(object_type: str, object_id: str, session: AsyncSession = Depends(get_session)) -> list[ProvenanceEventOut]:
    stmt = select(ProvenanceEvent).where(ProvenanceEvent.object_type == object_type, ProvenanceEvent.object_id == object_id).order_by(ProvenanceEvent.created_at.desc())
    result = await session.execute(stmt)
    return [ProvenanceEventOut.model_validate(row) for row in result.scalars().all()]
