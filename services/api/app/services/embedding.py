from __future__ import annotations
import hashlib
import math
from collections.abc import Iterable


def deterministic_embedding(text: str, *, dim: int = 384) -> list[float]:
    """Deterministic normalized embedding fallback.

    This is not a semantic model. It is a stable local fallback so ingestion, tests,
    and Qdrant integration run without bundled model weights. Production should replace
    this with Qwen3-Embedding through a model service.
    """
    if dim <= 0:
        raise ValueError("embedding dimension must be positive")
    vector = [0.0 for _ in range(dim)]
    tokens = text.lower().split()
    if not tokens:
        return vector
    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        for i in range(0, len(digest), 2):
            idx = int.from_bytes(digest[i:i + 2], "big") % dim
            sign = 1.0 if digest[i] % 2 == 0 else -1.0
            vector[idx] += sign
    norm = math.sqrt(sum(v * v for v in vector)) or 1.0
    return [v / norm for v in vector]


def cosine(a: Iterable[float], b: Iterable[float]) -> float:
    av = list(a)
    bv = list(b)
    if len(av) != len(bv):
        raise ValueError("vectors must have same dimension")
    denom = math.sqrt(sum(x * x for x in av)) * math.sqrt(sum(y * y for y in bv))
    if denom == 0:
        return 0.0
    return sum(x * y for x, y in zip(av, bv)) / denom
