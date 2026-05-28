from __future__ import annotations
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.app.core.config import get_settings
from services.api.app.core.db import get_session
from services.api.app.deps import get_vector_store
from services.api.app.domain.enums import ContentReviewStatus
from services.api.app.models import ContentBatch, ContentExport, ContentItem, ContentReviewEvent, ContentTemplate
from services.api.app.schemas import (
    ContentBatchCreate,
    ContentBatchOut,
    ContentExportOut,
    ContentExportRequest,
    ContentGenerateRequest,
    ContentItemOut,
    ContentReviewDecision,
    ContentReviewEventOut,
    ContentTemplateCreate,
    ContentTemplateOut,
)
from services.api.app.services.content_export import export_items_to_file
from services.api.app.services.content_factory import (
    create_content_batch,
    generate_content,
    list_content_items,
    run_content_batch,
)
from services.api.app.services.content_templates import DEFAULT_TEMPLATES

router = APIRouter(prefix="/content", tags=["content-factory"])


@router.post("/generate", response_model=ContentItemOut)
async def generate(payload: ContentGenerateRequest, session: AsyncSession = Depends(get_session)) -> ContentItemOut:
    return await generate_content(
        session,
        request=payload,
        settings=get_settings(),
        vector_store=get_vector_store(),
    )


@router.get("/templates", response_model=list[ContentTemplateOut])
async def list_templates(session: AsyncSession = Depends(get_session)) -> list[ContentTemplateOut]:
    result = await session.execute(select(ContentTemplate).where(ContentTemplate.active.is_(True)).order_by(ContentTemplate.name))
    db_templates = [ContentTemplateOut.model_validate(row) for row in result.scalars().all()]
    defaults = [ContentTemplateOut(**template.to_dict()) for template in DEFAULT_TEMPLATES]
    names = {template.name for template in db_templates}
    return db_templates + [template for template in defaults if template.name not in names]


@router.post("/templates", response_model=ContentTemplateOut)
async def create_template(payload: ContentTemplateCreate, session: AsyncSession = Depends(get_session)) -> ContentTemplateOut:
    template = ContentTemplate(**payload.model_dump())
    session.add(template)
    await session.commit()
    await session.refresh(template)
    return ContentTemplateOut.model_validate(template)


@router.post("/batches", response_model=ContentBatchOut)
async def create_batch(payload: ContentBatchCreate, session: AsyncSession = Depends(get_session)) -> ContentBatchOut:
    try:
        batch = await create_content_batch(session, payload, get_settings())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return ContentBatchOut.model_validate(batch)


@router.get("/batches", response_model=list[ContentBatchOut])
async def list_batches(
    limit: int = Query(default=50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
) -> list[ContentBatchOut]:
    result = await session.execute(select(ContentBatch).order_by(ContentBatch.created_at.desc()).limit(limit))
    return [ContentBatchOut.model_validate(row) for row in result.scalars().all()]


@router.post("/batches/{batch_id}/run", response_model=ContentBatchOut)
async def run_batch(batch_id: str, session: AsyncSession = Depends(get_session)) -> ContentBatchOut:
    batch = await session.get(ContentBatch, batch_id)
    if batch is None:
        raise HTTPException(status_code=404, detail="content batch not found")
    batch = await run_content_batch(session, batch=batch, settings=get_settings(), vector_store=get_vector_store())
    return ContentBatchOut.model_validate(batch)


@router.get("/items", response_model=list[ContentItemOut])
async def items(
    batch_id: str | None = None,
    review_status: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
) -> list[ContentItemOut]:
    rows = await list_content_items(session, batch_id=batch_id, review_status=review_status, limit=limit)
    return [ContentItemOut.model_validate(row) for row in rows]


@router.get("/items/{item_id}", response_model=ContentItemOut)
async def get_item(item_id: str, session: AsyncSession = Depends(get_session)) -> ContentItemOut:
    item = await session.get(ContentItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="content item not found")
    return ContentItemOut.model_validate(item)


@router.post("/items/{item_id}/review", response_model=ContentReviewEventOut)
async def review_item(
    item_id: str,
    payload: ContentReviewDecision,
    session: AsyncSession = Depends(get_session),
) -> ContentReviewEventOut:
    item = await session.get(ContentItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="content item not found")
    item.review_status = payload.decision.value
    event = ContentReviewEvent(
        item_id=item.id,
        reviewer_id=payload.reviewer_id,
        decision=payload.decision.value,
        reason=payload.reason,
        checklist=payload.checklist,
    )
    session.add(event)
    await session.commit()
    await session.refresh(event)
    return ContentReviewEventOut.model_validate(event)


@router.post("/exports", response_model=ContentExportOut)
async def create_export(payload: ContentExportRequest, session: AsyncSession = Depends(get_session)) -> ContentExportOut:
    rows = await list_content_items(
        session,
        batch_id=payload.batch_id,
        review_status=payload.review_status.value if payload.review_status else None,
        limit=5000,
    )
    settings = get_settings()
    stem = f"atman_content_{payload.batch_id or 'all'}_{payload.export_format.value}"
    export_payload = export_items_to_file(
        rows,
        export_format=payload.export_format.value,
        export_dir=Path(settings.content_export_dir),
        stem=stem,
    )
    for item in rows:
        item.export_status = "EXPORTED"
    export = ContentExport(
        batch_id=payload.batch_id,
        export_format=payload.export_format.value,
        file_path=str(export_payload.path),
        item_count=export_payload.item_count,
        manifest=export_payload.manifest,
    )
    session.add(export)
    await session.commit()
    await session.refresh(export)
    return ContentExportOut.model_validate(export)


@router.get("/exports", response_model=list[ContentExportOut])
async def list_exports(
    limit: int = Query(default=50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
) -> list[ContentExportOut]:
    result = await session.execute(select(ContentExport).order_by(ContentExport.created_at.desc()).limit(limit))
    return [ContentExportOut.model_validate(row) for row in result.scalars().all()]


@router.get("/exports/{export_id}/download")
async def download_export(export_id: str, session: AsyncSession = Depends(get_session)) -> FileResponse:
    export = await session.get(ContentExport, export_id)
    if export is None:
        raise HTTPException(status_code=404, detail="export not found")
    path = Path(export.file_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="export file missing on disk")
    return FileResponse(path, filename=path.name)
