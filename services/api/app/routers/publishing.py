from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.app.core.db import get_session
from services.api.app.models import ContentPublication, PublishingChannel, ProductEvent
from services.api.app.schemas import PublicationCreateRequest, PublicationOut, PublishingChannelCreate, PublishingChannelOut

router = APIRouter(prefix="/publishing", tags=["publishing-v1.0.5"])


@router.post("/channels", response_model=PublishingChannelOut)
async def create_channel(payload: PublishingChannelCreate, session: AsyncSession = Depends(get_session)) -> PublishingChannelOut:
    row = PublishingChannel(**payload.model_dump())
    session.add(row)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=409, detail="publishing channel already exists") from exc
    await session.refresh(row)
    return PublishingChannelOut.model_validate(row)


@router.get("/channels", response_model=list[PublishingChannelOut])
async def list_channels(session: AsyncSession = Depends(get_session)) -> list[PublishingChannelOut]:
    result = await session.execute(select(PublishingChannel).order_by(PublishingChannel.name.asc()))
    return [PublishingChannelOut.model_validate(row) for row in result.scalars().all()]


@router.post("/items", response_model=PublicationOut)
async def create_publication(payload: PublicationCreateRequest, session: AsyncSession = Depends(get_session)) -> PublicationOut:
    scheduled = datetime.fromisoformat(payload.scheduled_at) if payload.scheduled_at else None
    published = datetime.now(timezone.utc) if payload.status == "PUBLISHED" else None
    row = ContentPublication(
        **payload.model_dump(exclude={"scheduled_at"}),
        scheduled_at=scheduled,
        published_at=published,
    )
    session.add(row)
    await session.flush()
    session.add(ProductEvent(event_type="publication_created", object_type="content_publication", object_id=row.id, event_metadata={"status": row.status, "channel_id": row.channel_id}))
    await session.commit()
    await session.refresh(row)
    return PublicationOut.model_validate(row)


@router.get("/items", response_model=list[PublicationOut])
async def list_publications(
    status: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
) -> list[PublicationOut]:
    stmt = select(ContentPublication).order_by(ContentPublication.created_at.desc()).limit(limit)
    if status:
        stmt = select(ContentPublication).where(ContentPublication.status == status).order_by(ContentPublication.created_at.desc()).limit(limit)
    result = await session.execute(stmt)
    return [PublicationOut.model_validate(row) for row in result.scalars().all()]


@router.post("/items/{publication_id}/publish", response_model=PublicationOut)
async def publish_item(publication_id: str, session: AsyncSession = Depends(get_session)) -> PublicationOut:
    row = await session.get(ContentPublication, publication_id)
    if row is None:
        raise HTTPException(status_code=404, detail="publication not found")
    row.status = "PUBLISHED"
    row.published_at = datetime.now(timezone.utc)
    session.add(ProductEvent(event_type="publication_published", object_type="content_publication", object_id=row.id, event_metadata={"title": row.title}))
    await session.commit()
    await session.refresh(row)
    return PublicationOut.model_validate(row)
