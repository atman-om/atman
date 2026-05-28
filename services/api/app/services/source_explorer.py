from __future__ import annotations

from dataclasses import dataclass
from typing import Any


PUBLIC_RIGHTS = {"PUBLIC_DOMAIN_VERIFIED", "OPEN_LICENSE_VERIFIED", "LICENSED_VERIFIED"}
PUBLIC_STATUSES = {"APPROVED_Z2", "INDEXED"}


@dataclass(frozen=True)
class SourceExplorerResult:
    query: str | None
    total: int
    sources: list[dict[str, Any]]
    chunks: list[dict[str, Any]]
    filters: dict[str, Any]


def source_rights_explanation(source: Any) -> dict[str, Any]:
    rights = source.rights_status
    return {
        "rights_status": rights,
        "public_visible": rights in PUBLIC_RIGHTS and source.ingestion_status in PUBLIC_STATUSES,
        "allowed_uses": {
            "display_metadata": rights in PUBLIC_RIGHTS,
            "display_chunks": rights in PUBLIC_RIGHTS and source.ingestion_status in PUBLIC_STATUSES,
            "rag": rights in PUBLIC_RIGHTS and source.ingestion_status in PUBLIC_STATUSES,
            "training": rights in {"PUBLIC_DOMAIN_VERIFIED", "OPEN_LICENSE_VERIFIED", "USER_OWNED"},
        },
    }


def chunk_to_payload(chunk: Any, *, query: str | None = None) -> dict[str, Any]:
    text = chunk.chunk_text
    highlight = build_highlight(text, query) if query else None
    return {
        "id": chunk.id,
        "source_id": chunk.source_id,
        "chunk_text": text,
        "token_count": chunk.token_count,
        "chunk_order": chunk.chunk_order,
        "citation_locator": chunk.citation_locator or {},
        "quality_score": chunk.quality_score,
        "review_status": chunk.review_status,
        "highlight": highlight,
    }


def source_to_payload(source: Any, *, chunk_count: int = 0, matched_chunk_count: int = 0, locators: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {
        "id": source.id,
        "title": source.title,
        "source_type": source.source_type,
        "language": source.language,
        "rights_status": source.rights_status,
        "ingestion_status": source.ingestion_status,
        "tradition_scope": source.tradition_scope or [],
        "source_metadata": source.source_metadata or {},
        "chunk_count": chunk_count,
        "matched_chunk_count": matched_chunk_count,
        "locators": locators or [],
        "created_at": source.created_at.isoformat() if source.created_at else None,
    }


def build_highlight(text: str, query: str | None, *, radius: int = 96) -> str | None:
    if not query:
        return None
    low = text.lower()
    q = query.lower().strip()
    idx = low.find(q)
    if idx < 0:
        words = [w for w in q.split() if len(w) >= 3]
        idx = min([low.find(w) for w in words if low.find(w) >= 0] or [-1])
    if idx < 0:
        return text[: radius * 2].strip()
    start = max(0, idx - radius)
    end = min(len(text), idx + len(q) + radius)
    prefix = "…" if start else ""
    suffix = "…" if end < len(text) else ""
    return f"{prefix}{text[start:end].strip()}{suffix}"


async def search_sources(
    session,
    *,
    query: str | None,
    language: str | None,
    rights_status: list[str],
    ingestion_status: list[str],
    public_only: bool,
    limit: int,
    persist_query: bool = True,
) -> SourceExplorerResult:
    from sqlalchemy import and_, func, or_, select
    from services.api.app.models import Chunk, Source, SourceExplorerQuery

    source_conditions = []
    if public_only:
        source_conditions.append(Source.rights_status.in_(sorted(PUBLIC_RIGHTS)))
        source_conditions.append(Source.ingestion_status.in_(sorted(PUBLIC_STATUSES)))
    if language:
        source_conditions.append(Source.language == language)
    if rights_status:
        source_conditions.append(Source.rights_status.in_(rights_status))
    if ingestion_status:
        source_conditions.append(Source.ingestion_status.in_(ingestion_status))
    if query:
        like = f"%{query}%"
        source_conditions.append(or_(Source.title.ilike(like), Source.source_type.ilike(like)))

    source_stmt = select(Source).where(and_(*source_conditions)) if source_conditions else select(Source)
    source_stmt = source_stmt.order_by(Source.created_at.desc()).limit(limit)
    source_result = await session.execute(source_stmt)
    sources = list(source_result.scalars().all())

    chunk_conditions = []
    if sources:
        chunk_conditions.append(Chunk.source_id.in_([s.id for s in sources]))
    if query:
        chunk_conditions.append(Chunk.chunk_text.ilike(f"%{query}%"))
    chunk_stmt = select(Chunk)
    if chunk_conditions:
        chunk_stmt = chunk_stmt.where(and_(*chunk_conditions))
    elif public_only and not sources:
        chunk_stmt = chunk_stmt.where(False)
    chunk_stmt = chunk_stmt.order_by(Chunk.chunk_order).limit(limit * 4)
    chunk_result = await session.execute(chunk_stmt)
    chunks = list(chunk_result.scalars().all())

    source_ids = {s.id for s in sources} | {c.source_id for c in chunks}
    if source_ids - {s.id for s in sources}:
        extra_result = await session.execute(select(Source).where(Source.id.in_(source_ids - {s.id for s in sources})))
        sources.extend(extra_result.scalars().all())

    count_map: dict[str, int] = {}
    if source_ids:
        count_result = await session.execute(select(Chunk.source_id, func.count(Chunk.id)).where(Chunk.source_id.in_(source_ids)).group_by(Chunk.source_id))
        count_map = {source_id: int(count) for source_id, count in count_result.all()}

    matched_count: dict[str, int] = {}
    locators: dict[str, list[dict[str, Any]]] = {}
    for chunk in chunks:
        matched_count[chunk.source_id] = matched_count.get(chunk.source_id, 0) + 1
        locators.setdefault(chunk.source_id, [])
        loc = chunk.citation_locator or {}
        if loc and loc not in locators[chunk.source_id]:
            locators[chunk.source_id].append(loc)

    source_payloads = [
        source_to_payload(src, chunk_count=count_map.get(src.id, 0), matched_chunk_count=matched_count.get(src.id, 0), locators=locators.get(src.id, [])[:10])
        for src in sources
    ]
    chunk_payloads = [chunk_to_payload(chunk, query=query) for chunk in chunks]
    filters = {"language": language, "rights_status": rights_status, "ingestion_status": ingestion_status, "public_only": public_only, "limit": limit}

    if persist_query:
        session.add(SourceExplorerQuery(query=query, filters=filters, result_count=len(source_payloads), public=public_only))
        await session.commit()

    return SourceExplorerResult(query=query, total=len(source_payloads), sources=source_payloads, chunks=chunk_payloads, filters=filters)


async def get_source_detail(session, *, source_id: str, public_only: bool = True) -> dict[str, Any] | None:
    from sqlalchemy import select
    from services.api.app.models import Chunk, Source

    source = await session.get(Source, source_id)
    if source is None:
        return None
    if public_only and not (source.rights_status in PUBLIC_RIGHTS and source.ingestion_status in PUBLIC_STATUSES):
        return None
    chunks_result = await session.execute(select(Chunk).where(Chunk.source_id == source_id).order_by(Chunk.chunk_order))
    chunks = list(chunks_result.scalars().all())
    return {
        "source": source_to_payload(source, chunk_count=len(chunks), matched_chunk_count=len(chunks), locators=[c.citation_locator or {} for c in chunks if c.citation_locator][:20]),
        "chunks": [chunk_to_payload(chunk) for chunk in chunks],
        "rights_explanation": source_rights_explanation(source),
        "provenance": {
            "checksum_sha256": source.checksum_sha256,
            "source_metadata": source.source_metadata or {},
            "created_at": source.created_at.isoformat() if source.created_at else None,
            "updated_at": source.updated_at.isoformat() if source.updated_at else None,
        },
    }
