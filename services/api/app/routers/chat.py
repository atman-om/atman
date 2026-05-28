from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.app.core.config import get_settings
from services.api.app.core.db import get_session
from services.api.app.deps import get_vector_store
from services.api.app.models import ChatFeedback, ChatMessage, ChatRetrievalTrace, ChatSession, ModelUsageLog, ProductEvent
from services.api.app.schemas import (
    ChatDebugOut,
    ChatFeedbackOut,
    ChatFeedbackRequest,
    ChatMessageOut,
    ChatMessageSend,
    ChatSessionCreate,
    ChatSessionDetailOut,
    ChatSessionOut,
    ChatTurnOut,
)
from services.api.app.services.chatbot import generate_chat_answer

router = APIRouter(prefix="/chat", tags=["chatbot-v1.0.5"])


@router.post("/sessions", response_model=ChatSessionOut)
async def create_session(payload: ChatSessionCreate, session: AsyncSession = Depends(get_session)) -> ChatSessionOut:
    title = payload.title or "Atman Chat"
    row = ChatSession(**payload.model_dump(exclude={"title"}), title=title)
    session.add(row)
    await session.flush()
    session.add(ProductEvent(event_type="chat_session_created", actor_id=row.user_id, object_type="chat_session", object_id=row.id, event_metadata={"mode": row.mode}))
    await session.commit()
    await session.refresh(row)
    return ChatSessionOut.model_validate(row)


@router.get("/sessions", response_model=list[ChatSessionOut])
async def list_sessions(
    user_id: str | None = None,
    limit: int = Query(default=50, ge=1, le=250),
    session: AsyncSession = Depends(get_session),
) -> list[ChatSessionOut]:
    stmt = select(ChatSession).order_by(ChatSession.updated_at.desc()).limit(limit)
    if user_id:
        stmt = select(ChatSession).where(ChatSession.user_id == user_id).order_by(ChatSession.updated_at.desc()).limit(limit)
    result = await session.execute(stmt)
    return [ChatSessionOut.model_validate(row) for row in result.scalars().all()]


@router.get("/sessions/{session_id}", response_model=ChatSessionDetailOut)
async def get_session_detail(session_id: str, session: AsyncSession = Depends(get_session)) -> ChatSessionDetailOut:
    chat = await session.get(ChatSession, session_id)
    if chat is None:
        raise HTTPException(status_code=404, detail="chat session not found")
    result = await session.execute(select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc()))
    return ChatSessionDetailOut(session=ChatSessionOut.model_validate(chat), messages=[ChatMessageOut.model_validate(row) for row in result.scalars().all()])


@router.post("/sessions/{session_id}/messages", response_model=ChatTurnOut)
async def send_message(session_id: str, payload: ChatMessageSend, session: AsyncSession = Depends(get_session)) -> ChatTurnOut:
    settings = get_settings()
    chat = await session.get(ChatSession, session_id)
    if chat is None:
        raise HTTPException(status_code=404, detail="chat session not found")
    citation_mode = payload.citation_mode or chat.citation_mode or settings.chat_default_citation_mode
    user_msg = ChatMessage(session_id=session_id, role="user", content=payload.message, citation_mode=citation_mode)
    session.add(user_msg)
    await session.flush()
    generated = await generate_chat_answer(
        session,
        question=payload.message,
        top_k=payload.top_k,
        citation_mode=citation_mode,
        settings=settings,
        vector_store=get_vector_store(),
        chat_session_id=session_id,
        user_id=chat.user_id,
    )
    assistant_msg = ChatMessage(
        session_id=session_id,
        role="assistant",
        content=generated["answer"],
        model_name=generated["model_name"],
        provider=generated["provider"],
        citation_mode=citation_mode,
        visible_citations=generated["visible_citations"],
        internal_evidence=generated["internal_evidence"],
        safety_report=generated["safety_report"],
        latency_ms=generated["latency_ms"],
        usage=generated["usage"],
    )
    session.add(assistant_msg)
    await session.flush()
    trace = ChatRetrievalTrace(
        message_id=assistant_msg.id,
        query=payload.message,
        retrieved_chunks=generated["trace_payload"]["retrieved_chunks"],
        canonical_evidence=generated["trace_payload"]["canonical_evidence"],
        claim_checks=generated["trace_payload"]["claim_checks"],
        trace_report={"request_metadata": payload.request_metadata, "citation_mode": citation_mode},
    )
    session.add(trace)
    session.add(ProductEvent(event_type="chat_message_answered", actor_id=chat.user_id, object_type="chat_message", object_id=assistant_msg.id, event_metadata={"provider": generated["provider"], "usage": generated["usage"]}))
    await session.commit()
    await session.refresh(user_msg)
    await session.refresh(assistant_msg)
    return ChatTurnOut(
        user_message=ChatMessageOut.model_validate(user_msg),
        assistant_message=ChatMessageOut.model_validate(assistant_msg),
        trace_id=trace.id,
        usage_log_id=generated["usage_log_id"],
        ui_hints={"citation_mode": citation_mode, "show_feedback": settings.chat_enable_public_feedback},
    )


@router.post("/messages/{message_id}/feedback", response_model=ChatFeedbackOut)
async def feedback(message_id: str, payload: ChatFeedbackRequest, session: AsyncSession = Depends(get_session)) -> ChatFeedbackOut:
    msg = await session.get(ChatMessage, message_id)
    if msg is None:
        raise HTTPException(status_code=404, detail="message not found")
    row = ChatFeedback(message_id=message_id, **payload.model_dump())
    session.add(row)
    session.add(ProductEvent(event_type="chat_feedback_created", actor_id=payload.user_id, object_type="chat_message", object_id=message_id, event_metadata={"rating": payload.rating}))
    await session.commit()
    await session.refresh(row)
    return ChatFeedbackOut.model_validate(row)


@router.get("/debug/{message_id}", response_model=ChatDebugOut)
async def debug_message(message_id: str, session: AsyncSession = Depends(get_session)) -> ChatDebugOut:
    msg = await session.get(ChatMessage, message_id)
    if msg is None:
        raise HTTPException(status_code=404, detail="message not found")
    trace_result = await session.execute(select(ChatRetrievalTrace).where(ChatRetrievalTrace.message_id == message_id).order_by(ChatRetrievalTrace.created_at.desc()).limit(1))
    trace = trace_result.scalars().first()
    usage_result = await session.execute(select(ModelUsageLog).where(ModelUsageLog.session_id == msg.session_id).order_by(ModelUsageLog.created_at.desc()).limit(1))
    usage = usage_result.scalars().first()
    return ChatDebugOut(
        message=ChatMessageOut.model_validate(msg),
        retrieval_trace={"retrieved_chunks": trace.retrieved_chunks, "trace_report": trace.trace_report} if trace else None,
        model_usage={"provider": usage.provider, "model_name": usage.model_name, "estimated_cost": usage.estimated_cost, "usage": usage.usage_metadata} if usage else None,
        claim_checks=trace.claim_checks if trace else [],
    )
