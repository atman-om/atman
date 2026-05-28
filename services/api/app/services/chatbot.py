from __future__ import annotations

from typing import Any
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from services.api.app.core.config import Settings
from services.api.app.models import ChatRetrievalTrace, ModelUsageLog
from services.api.app.schemas import Citation
from services.api.app.services.model_gateway import estimate_cost, estimate_tokens, select_model_route
from services.api.app.services.rag import RetrievedChunk, generate_grounded_answer, retrieve_chunks
from services.api.app.services.safety import evaluate_query_and_answer
from services.api.app.services.vector_store import QdrantStore


def citations_from_chunks(chunks: list[RetrievedChunk], citation_mode: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    internal: list[dict[str, Any]] = []
    for chunk in chunks:
        internal.append({
            "chunk_id": chunk.chunk_id,
            "source_id": chunk.source_id,
            "title": chunk.title,
            "locator": chunk.locator,
            "score": round(float(chunk.score), 4),
            "text_preview": chunk.text[:500],
            "evidence_grade": "B" if chunk.score >= 0.7 else "C" if chunk.score > 0 else "D",
        })
    if citation_mode == "hidden":
        return [], internal
    if citation_mode == "source":
        visible = [
            {"title": item["title"], "locator": item["locator"], "evidence_grade": item["evidence_grade"]}
            for item in internal
        ]
        return visible, internal
    return internal, internal


async def generate_chat_answer(
    session: AsyncSession,
    *,
    question: str,
    top_k: int,
    citation_mode: str,
    settings: Settings,
    vector_store: QdrantStore | None,
    chat_session_id: str | None = None,
    user_id: str | None = None,
) -> dict[str, Any]:
    chunks = await retrieve_chunks(session, question=question, top_k=top_k, settings=settings, vector_store=vector_store)
    answer, runtime_meta = await generate_grounded_answer(question=question, chunks=chunks, settings=settings)
    safety = evaluate_query_and_answer(question, answer, citations_count=len(chunks))
    visible, internal = citations_from_chunks(chunks, citation_mode)
    input_tokens = estimate_tokens(question + "\n" + "\n".join(chunk.text for chunk in chunks))
    usage = runtime_meta.get("usage") if isinstance(runtime_meta.get("usage"), dict) else {}
    output_tokens = int(usage.get("completion_tokens") or usage.get("output_tokens") or estimate_tokens(answer))
    prompt_tokens = int(usage.get("prompt_tokens") or usage.get("input_tokens") or input_tokens)
    estimated_cost = estimate_cost(settings, input_tokens=prompt_tokens, output_tokens=output_tokens)
    route = select_model_route(settings, "chat")
    usage_row = ModelUsageLog(
        provider=str(runtime_meta.get("provider") or route.provider),
        model_name=str(runtime_meta.get("model_name") or settings.runtime_model),
        feature="chat",
        user_id=user_id,
        session_id=chat_session_id,
        input_tokens=prompt_tokens,
        output_tokens=output_tokens,
        estimated_cost=estimated_cost,
        currency=settings.billing_currency,
        latency_ms=int(runtime_meta.get("latency_ms") or 0),
        status="COMPLETED" if safety.allowed else "SAFETY_FLAGGED",
        usage_metadata={"route": route.__dict__, "provider_usage": usage, "warnings": runtime_meta.get("warnings", [])},
    )
    session.add(usage_row)
    await session.flush()
    trace_id: str | None = None
    if settings.chat_store_retrieval_traces:
        trace = ChatRetrievalTrace(
            message_id=str(uuid4()),  # patched by caller after assistant message insert if needed
            query=question,
            retrieved_chunks=internal,
            canonical_evidence=internal,
            claim_checks=[],
            trace_report={"citation_mode": citation_mode, "safety": safety.__dict__, "route": route.__dict__},
        )
        # Caller may create the durable trace with actual message id; return trace payload here.
        trace_id = trace.id
    return {
        "answer": answer,
        "visible_citations": visible,
        "internal_evidence": internal,
        "safety_report": {"allowed": safety.allowed, "flags": safety.flags, "reason": safety.reason},
        "model_name": settings.runtime_model,
        "provider": str(runtime_meta.get("provider") or route.provider),
        "latency_ms": int(runtime_meta.get("latency_ms") or 0),
        "usage": {"input_tokens": prompt_tokens, "output_tokens": output_tokens, "estimated_cost": estimated_cost, "currency": settings.billing_currency},
        "usage_log_id": usage_row.id,
        "trace_id": trace_id,
        "trace_payload": {"retrieved_chunks": internal, "canonical_evidence": internal, "claim_checks": [], "route": route.__dict__},
    }
