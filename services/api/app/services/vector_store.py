from __future__ import annotations
from dataclasses import dataclass
from typing import Any

from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams
from qdrant_client.http.exceptions import UnexpectedResponse


@dataclass(frozen=True)
class VectorHit:
    vector_id: str
    score: float
    payload: dict[str, Any]


class QdrantStore:
    def __init__(self, *, url: str, collection: str, dim: int) -> None:
        self.client = AsyncQdrantClient(url=url)
        self.collection = collection
        self.dim = dim

    async def ensure_collection(self) -> None:
        collections = await self.client.get_collections()
        if any(c.name == self.collection for c in collections.collections):
            return
        await self.client.create_collection(
            collection_name=self.collection,
            vectors_config=VectorParams(size=self.dim, distance=Distance.COSINE),
        )

    async def upsert(self, *, vector_id: str, vector: list[float], payload: dict[str, Any]) -> None:
        await self.ensure_collection()
        await self.client.upsert(
            collection_name=self.collection,
            points=[PointStruct(id=vector_id, vector=vector, payload=payload)],
        )

    async def search(self, *, vector: list[float], top_k: int) -> list[VectorHit]:
        await self.ensure_collection()
        results = await self.client.search(
            collection_name=self.collection,
            query_vector=vector,
            limit=top_k,
            with_payload=True,
        )
        return [VectorHit(vector_id=str(item.id), score=float(item.score), payload=dict(item.payload or {})) for item in results]
