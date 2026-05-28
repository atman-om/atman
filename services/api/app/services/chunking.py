from __future__ import annotations
from dataclasses import dataclass
import re

_TOKEN_RE = re.compile(r"\S+", re.UNICODE)
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[।.!?])\s+", re.UNICODE)


@dataclass(frozen=True)
class TextChunk:
    text: str
    token_count: int
    order: int


def count_tokens(text: str) -> int:
    return len(_TOKEN_RE.findall(text))


def normalize_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip()


def chunk_text(text: str, *, max_tokens: int = 420, overlap_tokens: int = 60) -> list[TextChunk]:
    if max_tokens <= 0:
        raise ValueError("max_tokens must be positive")
    if overlap_tokens < 0:
        raise ValueError("overlap_tokens cannot be negative")
    if overlap_tokens >= max_tokens:
        raise ValueError("overlap_tokens must be smaller than max_tokens")

    normalized = normalize_text(text)
    if not normalized:
        return []

    sentences = []
    for para in normalized.split("\n"):
        para = para.strip()
        if not para:
            continue
        sentences.extend([s.strip() for s in _SENTENCE_SPLIT_RE.split(para) if s.strip()])

    chunks: list[TextChunk] = []
    current: list[str] = []
    current_tokens = 0

    def flush() -> None:
        nonlocal current, current_tokens
        if current:
            body = " ".join(current).strip()
            chunks.append(TextChunk(text=body, token_count=count_tokens(body), order=len(chunks)))
            if overlap_tokens > 0:
                words = _TOKEN_RE.findall(body)
                tail = " ".join(words[-overlap_tokens:])
                current = [tail] if tail else []
                current_tokens = count_tokens(tail)
            else:
                current = []
                current_tokens = 0

    for sentence in sentences:
        sentence_tokens = count_tokens(sentence)
        if sentence_tokens > max_tokens:
            words = _TOKEN_RE.findall(sentence)
            step = max_tokens - overlap_tokens
            for start in range(0, len(words), step):
                piece = " ".join(words[start:start + max_tokens])
                if piece:
                    if current:
                        flush()
                    chunks.append(TextChunk(text=piece, token_count=count_tokens(piece), order=len(chunks)))
            current = []
            current_tokens = 0
            continue
        if current_tokens + sentence_tokens > max_tokens:
            flush()
        current.append(sentence)
        current_tokens += sentence_tokens

    if current:
        body = " ".join(current).strip()
        if not chunks or chunks[-1].text != body:
            chunks.append(TextChunk(text=body, token_count=count_tokens(body), order=len(chunks)))

    return chunks
