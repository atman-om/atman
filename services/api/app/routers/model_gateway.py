from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.app.core.config import get_settings
from services.api.app.core.db import get_session
from services.api.app.models import ModelUsageLog
from services.api.app.schemas import ModelUsageLogOut, RemoteModelProviderOut
from services.api.app.services.model_gateway import remote_provider_status, select_model_route

router = APIRouter(prefix="/models/remote", tags=["remote-model-gateway-v1.0.5"])


@router.get("/providers", response_model=list[RemoteModelProviderOut])
async def providers() -> list[RemoteModelProviderOut]:
    status = await remote_provider_status(get_settings())
    return [RemoteModelProviderOut(**{k: status[k] for k in RemoteModelProviderOut.model_fields.keys() if k in status})]


@router.get("/status", response_model=RemoteModelProviderOut)
async def status() -> RemoteModelProviderOut:
    status = await remote_provider_status(get_settings())
    return RemoteModelProviderOut(**{k: status[k] for k in RemoteModelProviderOut.model_fields.keys() if k in status})


@router.get("/route")
async def route(feature: str = "chat") -> dict[str, str]:
    selected = select_model_route(get_settings(), feature)
    return selected.__dict__


@router.get("/usage", response_model=list[ModelUsageLogOut])
async def usage(
    feature: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
) -> list[ModelUsageLogOut]:
    stmt = select(ModelUsageLog).order_by(ModelUsageLog.created_at.desc()).limit(limit)
    if feature:
        stmt = select(ModelUsageLog).where(ModelUsageLog.feature == feature).order_by(ModelUsageLog.created_at.desc()).limit(limit)
    result = await session.execute(stmt)
    return [ModelUsageLogOut.model_validate(row) for row in result.scalars().all()]


@router.get("/usage/summary")
async def usage_summary(session: AsyncSession = Depends(get_session)) -> dict[str, float | int]:
    result = await session.execute(
        select(
            func.count(ModelUsageLog.id),
            func.coalesce(func.sum(ModelUsageLog.input_tokens), 0),
            func.coalesce(func.sum(ModelUsageLog.output_tokens), 0),
            func.coalesce(func.sum(ModelUsageLog.estimated_cost), 0.0),
        )
    )
    count, input_tokens, output_tokens, cost = result.one()
    return {"calls": int(count), "input_tokens": int(input_tokens), "output_tokens": int(output_tokens), "estimated_cost": float(cost)}
