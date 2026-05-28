from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.app.core.config import get_settings
from services.api.app.core.db import get_session
from services.api.app.deps import get_vector_store
from services.api.app.models import Source
from services.api.app.schemas import PublicAskRequest, PublicAskResponse, SourceOut
from services.api.app.services.rag import answer_question
from services.api.app.services.source_explorer import PUBLIC_RIGHTS, PUBLIC_STATUSES

router = APIRouter(prefix="/public", tags=["public-app"])


@router.post("/ask", response_model=PublicAskResponse)
async def public_ask(payload: PublicAskRequest, session: AsyncSession = Depends(get_session)) -> PublicAskResponse:
    response = await answer_question(
        session,
        question=payload.question,
        top_k=payload.top_k,
        settings=get_settings(),
        vector_store=get_vector_store(),
        public_only=True,
    )
    ui_hints = {
        "mode": payload.mode,
        "show_citations": True,
        "show_feedback": True,
        "answer_language": payload.language,
    }
    return PublicAskResponse(
        answer=response.answer,
        citations=response.citations,
        safety_report=response.safety_report,
        model_name=response.model_name,
        latency_ms=response.latency_ms,
        ui_hints=ui_hints,
    )


@router.post("/ask/stream")
async def public_ask_stream(payload: PublicAskRequest, session: AsyncSession = Depends(get_session)) -> StreamingResponse:
    settings = get_settings()
    if not settings.public_enable_streaming:
        raise HTTPException(status_code=403, detail="streaming disabled")

    async def event_stream():
        response = await answer_question(
            session,
            question=payload.question,
            top_k=payload.top_k,
            settings=settings,
            vector_store=get_vector_store(),
            public_only=True,
        )
        yield f"event: meta\ndata: {json.dumps({'model_name': response.model_name, 'latency_ms': response.latency_ms}, ensure_ascii=False)}\n\n"
        for part in _split_stream(response.answer):
            yield f"event: token\ndata: {json.dumps({'text': part}, ensure_ascii=False)}\n\n"
        yield f"event: citations\ndata: {json.dumps([c.model_dump() for c in response.citations], ensure_ascii=False)}\n\n"
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/sources", response_model=list[SourceOut])
async def public_sources(session: AsyncSession = Depends(get_session)) -> list[SourceOut]:
    stmt = (
        select(Source)
        .where(Source.rights_status.in_(sorted(PUBLIC_RIGHTS)), Source.ingestion_status.in_(sorted(PUBLIC_STATUSES)))
        .order_by(Source.created_at.desc())
        .limit(50)
    )
    result = await session.execute(stmt)
    return [SourceOut.model_validate(row) for row in result.scalars().all()]


def _split_stream(text: str, size: int = 96) -> list[str]:
    parts: list[str] = []
    cur = ""
    for word in text.split(" "):
        candidate = f"{cur} {word}".strip()
        if len(candidate) > size and cur:
            parts.append(cur + " ")
            cur = word
        else:
            cur = candidate
    if cur:
        parts.append(cur)
    return parts
