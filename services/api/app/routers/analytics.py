from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.app.core.config import get_settings
from services.api.app.core.db import get_session
from services.api.app.models import (
    AcquisitionJob,
    AppUser,
    CanonicalPassage,
    CanonicalWork,
    ChatFeedback,
    ChatMessage,
    ChatSession,
    ContentItem,
    ContentPublication,
    ModelUsageLog,
    SourceSnapshot,
)
from services.api.app.schemas import AnalyticsOverviewOut, ProductReadinessOut

router = APIRouter(prefix="/analytics", tags=["analytics-v1.0.5"])


async def scalar_count(session: AsyncSession, model) -> int:  # type: ignore[no-untyped-def]
    result = await session.execute(select(func.count(model.id)))
    return int(result.scalar() or 0)


@router.get("/overview", response_model=AnalyticsOverviewOut)
async def overview(
    window_days: int = Query(default=30, ge=1, le=3650),
    session: AsyncSession = Depends(get_session),
) -> AnalyticsOverviewOut:
    usage = await session.execute(select(func.coalesce(func.sum(ModelUsageLog.input_tokens), 0), func.coalesce(func.sum(ModelUsageLog.output_tokens), 0), func.coalesce(func.sum(ModelUsageLog.estimated_cost), 0.0)))
    input_tokens, output_tokens, cost = usage.one()
    feedback = await session.execute(select(ChatFeedback.rating, func.count(ChatFeedback.id)).group_by(ChatFeedback.rating))
    feedback_by_rating = {rating: int(count) for rating, count in feedback.all()}
    return AnalyticsOverviewOut(
        window_days=window_days,
        chats={"sessions": await scalar_count(session, ChatSession), "messages": await scalar_count(session, ChatMessage), "feedback_by_rating": feedback_by_rating},
        corpus={"canonical_works": await scalar_count(session, CanonicalWork), "canonical_passages": await scalar_count(session, CanonicalPassage), "quarantine_snapshots": await scalar_count(session, SourceSnapshot)},
        content={"content_items": await scalar_count(session, ContentItem)},
        model_usage={"input_tokens": int(input_tokens), "output_tokens": int(output_tokens), "estimated_cost": float(cost), "currency": get_settings().billing_currency},
        publishing={"publications": await scalar_count(session, ContentPublication)},
        acquisition={"jobs": await scalar_count(session, AcquisitionJob)},
        billing={"estimated_model_cost": float(cost), "currency": get_settings().billing_currency},
    )


@router.get("/readiness", response_model=ProductReadinessOut)
async def product_readiness(session: AsyncSession = Depends(get_session)) -> ProductReadinessOut:
    settings = get_settings()
    users = await scalar_count(session, AppUser)
    works = await scalar_count(session, CanonicalWork)
    passages = await scalar_count(session, CanonicalPassage)
    sessions = await scalar_count(session, ChatSession)
    blockers: list[str] = []
    warnings: list[str] = []
    mode = settings.qwen_runtime_mode.strip().lower()
    if mode == "gemini":
        if not settings.gemini_base_url:
            blockers.append("gemini_base_url_not_configured")
        if not settings.resolved_gemini_api_key:
            blockers.append("gemini_api_key_not_configured")
    elif not settings.resolved_qwen_base_url:
        blockers.append("remote_qwen_base_url_not_configured")
    if mode != "gemini" and not settings.resolved_qwen_api_key:
        warnings.append("remote_qwen_api_key_not_configured")
    if works == 0 or passages == 0:
        warnings.append("canonical_corpus_seed_missing")
    checks = {
        "remote_qwen_mode": settings.qwen_runtime_mode,
        "provider": "gemini_api" if mode == "gemini" else settings.remote_qwen_default_provider,
        "model_id": settings.gemini_model_id if mode == "gemini" else settings.qwen_model_id,
        "users": users,
        "canonical_works": works,
        "canonical_passages": passages,
        "chat_sessions": sessions,
    }
    return ProductReadinessOut(version=settings.product_version, ready_for_demo=len(blockers) == 0, ready_for_public_beta=len(blockers) == 0 and works > 0 and passages > 0, checks=checks, blockers=blockers, warnings=warnings)
