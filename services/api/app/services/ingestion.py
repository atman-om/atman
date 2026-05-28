from __future__ import annotations
from dataclasses import dataclass
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.app.domain.enums import IngestionStatus
from services.api.app.models import Chunk, Embedding, Source
from services.api.app.services.chunking import chunk_text
from services.api.app.services.embedding import deterministic_embedding
from services.api.app.services.hashutil import sha256_text
from services.api.app.services.locator import chunk_locator
from services.api.app.services.vector_store import QdrantStore


@dataclass(frozen=True)
class IngestionReport:
    source_id: str
    chunks_created: int
    indexed: bool


async def ingest_plaintext_source(
    session: AsyncSession,
    *,
    source: Source,
    text: str,
    vector_store: QdrantStore | None,
    embedding_dim: int,
) -> IngestionReport:
    checksum = sha256_text(text)
    source.checksum_sha256 = source.checksum_sha256 or checksum
    source.ingestion_status = IngestionStatus.PARSED.value
    chunks = chunk_text(text)
    source.ingestion_status = IngestionStatus.CHUNKED.value
    session.add(source)
    await session.flush()

    base_locator = source.source_metadata.get("locator") if source.source_metadata else None
    created = 0
    indexed = False
    for piece in chunks:
        chunk = Chunk(
            source_id=source.id,
            chunk_text=piece.text,
            token_count=piece.token_count,
            chunk_order=piece.order,
            citation_locator=chunk_locator(base_locator, piece.order),
            quality_score=0.75,
            review_status="REVIEW_PENDING",
        )
        session.add(chunk)
        await session.flush()
        vector_id = chunk.id
        vector = deterministic_embedding(piece.text, dim=embedding_dim)
        if vector_store is not None:
            await vector_store.upsert(
                vector_id=vector_id,
                vector=vector,
                payload={
                    "chunk_id": chunk.id,
                    "source_id": source.id,
                    "title": source.title,
                    "locator": chunk.citation_locator,
                    "text_preview": piece.text[:500],
                },
            )
            indexed = True
        session.add(Embedding(chunk_id=chunk.id, embedding_model="Atman-RAG-QwenEmbedding-fallback", vector_id=vector_id))
        created += 1

    source.ingestion_status = IngestionStatus.INDEXED.value if indexed else IngestionStatus.EMBEDDED.value
    await session.commit()
    return IngestionReport(source_id=source.id, chunks_created=created, indexed=indexed)
