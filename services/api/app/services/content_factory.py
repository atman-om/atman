from __future__ import annotations

from statistics import mean
from typing import Any, cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.app.core.config import Settings
from services.api.app.domain.enums import ContentBatchStatus, ContentReviewStatus
from services.api.app.models import ContentBatch, ContentItem, ContentTemplate
from services.api.app.schemas import ContentBatchCreate, ContentGenerateRequest, ContentItemOut
from services.api.app.services.content_logic import build_drafts
from services.api.app.services.content_templates import get_default_template
from services.api.app.services.rag import generate_grounded_answer, retrieve_chunks
from services.api.app.services.vector_store import QdrantStore


async def _resolve_template_name(session: AsyncSession, template_id: str | None, content_type: str, language: str) -> str:
    if template_id:
        template = await session.get(ContentTemplate, template_id)
        if template is not None:
            return template.name
    return get_default_template(content_type, language).name


async def generate_content(
    session: AsyncSession,
    *,
    request: ContentGenerateRequest,
    settings: Settings,
    vector_store: QdrantStore | None,
) -> ContentItemOut:
    chunks = await retrieve_chunks(session, question=request.topic, top_k=5, settings=settings, vector_store=vector_store)
    template_name = await _resolve_template_name(session, request.template_id, request.content_type, request.language)
    grounded_answer, _runtime_meta = await generate_grounded_answer(question=request.topic, chunks=chunks, settings=settings, language=request.language)
    draft = build_drafts(request, chunks=chunks, settings=settings, template_name=template_name, grounded_answer=grounded_answer)[0]
    item = ContentItem(
        template_id=request.template_id,
        item_index=draft.item_index,
        title=draft.title,
        content_type=request.content_type,
        topic=request.topic,
        language=request.language,
        body=draft.body,
        source_chunk_ids=draft.provenance["source_chunk_ids"],
        quality_report=draft.quality_report,
        review_status=draft.quality_report["recommended_review_status"],
        provenance=draft.provenance,
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return ContentItemOut.model_validate(item)


async def create_content_batch(session: AsyncSession, payload: ContentBatchCreate, settings: Settings) -> ContentBatch:
    if payload.quantity > settings.content_max_batch_items:
        raise ValueError(f"quantity exceeds configured limit: {settings.content_max_batch_items}")
    batch = ContentBatch(
        name=payload.name,
        content_type=payload.content_type,
        topic=payload.topic,
        language=payload.language,
        difficulty=payload.difficulty,
        quantity=payload.quantity,
        template_id=payload.template_id,
        status=ContentBatchStatus.DRAFT.value,
        generation_config={**payload.generation_config, "source_required": payload.source_required},
        created_by=payload.created_by,
        metrics={},
    )
    session.add(batch)
    await session.commit()
    await session.refresh(batch)
    return batch


async def run_content_batch(
    session: AsyncSession,
    *,
    batch: ContentBatch,
    settings: Settings,
    vector_store: QdrantStore | None,
) -> ContentBatch:
    batch.status = ContentBatchStatus.RUNNING.value
    await session.commit()
    source_required = bool((batch.generation_config or {}).get("source_required", True))
    request = ContentBatchCreate(
        name=batch.name,
        content_type=cast(Any, batch.content_type),
        topic=batch.topic,
        language=batch.language,
        difficulty=cast(Any, batch.difficulty),
        quantity=batch.quantity,
        template_id=batch.template_id,
        source_required=source_required,
        generation_config=batch.generation_config or {},
        created_by=batch.created_by,
    )
    chunks = await retrieve_chunks(session, question=batch.topic, top_k=5, settings=settings, vector_store=vector_store)
    template_name = await _resolve_template_name(session, batch.template_id, batch.content_type, batch.language)
    grounded_answer, _runtime_meta = await generate_grounded_answer(question=batch.topic, chunks=chunks, settings=settings, language=batch.language)
    drafts = build_drafts(request, chunks=chunks, settings=settings, template_name=template_name, grounded_answer=grounded_answer)
    score_values: list[float] = []
    warning_count = 0
    for draft in drafts:
        status = draft.quality_report["recommended_review_status"]
        if status != ContentReviewStatus.REVIEW_PENDING.value:
            warning_count += 1
        score_values.append(float(draft.quality_report.get("score", 0.0)))
        item = ContentItem(
            batch_id=batch.id,
            template_id=batch.template_id,
            item_index=draft.item_index,
            title=draft.title,
            content_type=batch.content_type,
            topic=batch.topic,
            language=batch.language,
            body=draft.body,
            source_chunk_ids=draft.provenance["source_chunk_ids"],
            quality_report=draft.quality_report,
            review_status=status,
            provenance=draft.provenance,
        )
        session.add(item)
    batch.metrics = {
        "items_created": len(drafts),
        "sources_used": len(chunks),
        "warning_count": warning_count,
        "avg_quality_score": round(mean(score_values), 4) if score_values else 0.0,
        "model_family": settings.model_family,
        "content_model": settings.content_model,
    }
    batch.status = ContentBatchStatus.COMPLETED_WITH_WARNINGS.value if warning_count else ContentBatchStatus.COMPLETED.value
    await session.commit()
    await session.refresh(batch)
    return batch


async def list_content_items(
    session: AsyncSession,
    *,
    batch_id: str | None = None,
    review_status: str | None = None,
    limit: int = 100,
) -> list[ContentItem]:
    stmt = select(ContentItem).order_by(ContentItem.created_at.desc()).limit(limit)
    if batch_id:
        stmt = stmt.where(ContentItem.batch_id == batch_id)
    if review_status:
        stmt = stmt.where(ContentItem.review_status == review_status)
    result = await session.execute(stmt)
    return list(result.scalars().all())
