from __future__ import annotations
from dataclasses import dataclass
from time import perf_counter
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.app.core.config import Settings
from services.api.app.models import Chunk, RagQuery, Source
from services.api.app.schemas import Citation, RagQueryResponse, SafetyReport
from services.api.app.services.embedding import deterministic_embedding
from services.api.app.services.qwen_runtime import QwenRuntime, build_rag_messages
from services.api.app.services.safety import evaluate_query_and_answer
from services.api.app.services.source_explorer import PUBLIC_RIGHTS, PUBLIC_STATUSES
from services.api.app.services.vector_store import QdrantStore


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: str
    source_id: str
    title: str
    locator: dict[str, Any]
    score: float
    text: str


async def retrieve_chunks(
    session: AsyncSession,
    *,
    question: str,
    top_k: int,
    settings: Settings,
    vector_store: QdrantStore | None,
    public_only: bool = False,
) -> list[RetrievedChunk]:
    if vector_store is not None:
        vector = deterministic_embedding(question, dim=settings.embedding_dim)
        try:
            hits = await vector_store.search(vector=vector, top_k=top_k)
            retrieved: list[RetrievedChunk] = []
            for hit in hits:
                chunk_id = str(hit.payload.get("chunk_id", ""))
                if not chunk_id:
                    continue
                conditions = [Chunk.id == chunk_id]
                if public_only:
                    conditions.extend(
                        [
                            Source.rights_status.in_(sorted(PUBLIC_RIGHTS)),
                            Source.ingestion_status.in_(sorted(PUBLIC_STATUSES)),
                        ]
                    )
                row = await session.execute(select(Chunk, Source).join(Source, Chunk.source_id == Source.id).where(*conditions))
                result = row.first()
                if result is None:
                    continue
                chunk, source = result
                retrieved.append(
                    RetrievedChunk(
                        chunk_id=chunk.id,
                        source_id=source.id,
                        title=source.title,
                        locator=chunk.citation_locator,
                        score=hit.score,
                        text=chunk.chunk_text,
                    )
                )
            if retrieved:
                return retrieved
        except Exception:
            # Qdrant is non-critical in local scaffolds; fallback to lexical retrieval.
            pass

    terms = [t for t in question.lower().split() if len(t) > 2]
    lexical_stmt = select(Chunk, Source).join(Source, Chunk.source_id == Source.id)
    if public_only:
        lexical_stmt = lexical_stmt.where(
            Source.rights_status.in_(sorted(PUBLIC_RIGHTS)),
            Source.ingestion_status.in_(sorted(PUBLIC_STATUSES)),
        )
    result = await session.execute(lexical_stmt.limit(200))
    scored: list[RetrievedChunk] = []
    for chunk, source in result.all():
        hay = chunk.chunk_text.lower()
        score = sum(1 for term in terms if term in hay) / max(len(terms), 1)
        if score > 0 or len(scored) < top_k:
            scored.append(
                RetrievedChunk(
                    chunk_id=chunk.id,
                    source_id=source.id,
                    title=source.title,
                    locator=chunk.citation_locator,
                    score=float(score),
                    text=chunk.chunk_text,
                )
            )
    scored.sort(key=lambda item: item.score, reverse=True)
    return scored[:top_k]


def synthesize_hindi_answer(question: str, chunks: list[RetrievedChunk]) -> str:
    """Deterministic fallback synthesis retained for tests/offline mode."""
    if not chunks:
        return (
            "मेरे पास इस प्रश्न के लिए अभी पर्याप्त सत्यापित स्रोत नहीं हैं। "
            "Atman बिना स्रोत के शास्त्रीय दावा नहीं करेगा।"
        )
    bullet_lines = []
    for idx, chunk in enumerate(chunks[:4], start=1):
        preview = chunk.text.strip().replace("\n", " ")[:420]
        bullet_lines.append(f"{idx}. {preview}")
    return (
        "संक्षिप्त उत्तर: नीचे दिया गया उत्तर उपलब्ध सत्यापित स्रोत-खंडों पर आधारित प्रारम्भिक RAG उत्तर है।\n\n"
        f"प्रश्न: {question}\n\n"
        "स्रोत-आधारित संकेत:\n" + "\n".join(bullet_lines) + "\n\n"
        "नोट: यह local fallback synthesis है; production में Qwen runtime, reranker और NyayaBench verifier से final answer release होगा।"
    )


async def generate_grounded_answer(
    *,
    question: str,
    chunks: list[RetrievedChunk],
    settings: Settings,
    language: str = "hi",
) -> tuple[str, dict[str, Any]]:
    if settings.qwen_runtime_mode.strip().lower() == "deterministic":
        return synthesize_hindi_answer(question, chunks), {"provider": "deterministic_rag_synthesis"}
    source_blocks = [
        {
            "chunk_id": chunk.chunk_id,
            "source_id": chunk.source_id,
            "title": chunk.title,
            "locator": chunk.locator,
            "score": chunk.score,
            "text": chunk.text,
        }
        for chunk in chunks
    ]
    runtime = QwenRuntime(settings)
    result = await runtime.generate(build_rag_messages(question=question, source_blocks=source_blocks, language=language))
    return result.text, {
        "provider": result.provider,
        "model_name": result.model_name,
        "usage": result.usage,
        "warnings": result.warnings,
        "latency_ms": result.latency_ms,
    }


async def answer_question(
    session: AsyncSession,
    *,
    question: str,
    top_k: int,
    settings: Settings,
    vector_store: QdrantStore | None,
    public_only: bool = False,
) -> RagQueryResponse:
    started = perf_counter()
    chunks = await retrieve_chunks(
        session,
        question=question,
        top_k=top_k,
        settings=settings,
        vector_store=vector_store,
        public_only=public_only,
    )
    answer, runtime_meta = await generate_grounded_answer(question=question, chunks=chunks, settings=settings)
    safety = evaluate_query_and_answer(question, answer, citations_count=len(chunks))
    citations = [
        Citation(
            chunk_id=chunk.chunk_id,
            source_id=chunk.source_id,
            title=chunk.title,
            locator=chunk.locator,
            score=chunk.score,
            text_preview=chunk.text[:240],
        )
        for chunk in chunks
    ]
    latency_ms = int((perf_counter() - started) * 1000)
    row = RagQuery(
        question=question,
        answer=answer,
        model_name=settings.runtime_model,
        citations=[c.model_dump() for c in citations],
        safety_report={"allowed": safety.allowed, "flags": safety.flags, "reason": safety.reason, "runtime": runtime_meta},
        latency_ms=latency_ms,
    )
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return RagQueryResponse(
        query_id=row.id,
        answer=answer,
        citations=citations,
        safety_report=SafetyReport(allowed=safety.allowed, flags=safety.flags, reason=safety.reason),
        model_name=settings.runtime_model,
        latency_ms=latency_ms,
    )
