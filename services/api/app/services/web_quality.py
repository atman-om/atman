from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse
import re


@dataclass(frozen=True)
class WebQualityAssessment:
    score: float
    verdict: str
    components: dict[str, float | str | bool | int]
    allowed_usage: dict[str, bool | str]


TRAIN_ALLOWED_RIGHTS = {"PUBLIC_DOMAIN_VERIFIED", "LICENSED_VERIFIED", "OPEN_LICENSE_VERIFIED", "USER_OWNED"}
RAG_ALLOWED_RIGHTS = TRAIN_ALLOWED_RIGHTS | {"NO_TRAINING_ALLOWED"}


def allowed_usage_for_rights(rights_status: str) -> dict[str, bool | str]:
    rights = rights_status.upper()
    return {
        "store": rights not in {"REJECTED", "NO_STORAGE_ALLOWED"},
        "rag": rights in RAG_ALLOWED_RIGHTS,
        "train": rights in TRAIN_ALLOWED_RIGHTS,
        "quote": "limited" if rights in {"REFERENCE_ONLY", "NO_TRAINING_ALLOWED"} else rights in TRAIN_ALLOWED_RIGHTS,
    }


def score_web_source_text(text: str, *, url: str, rights_status: str, robots_status: str = "UNKNOWN") -> WebQualityAssessment:
    normalized = re.sub(r"\s+", " ", text).strip()
    parsed = urlparse(url)
    length_score = min(1.0, len(normalized) / 5000)
    devanagari_score = min(1.0, len(re.findall(r"[\u0900-\u097F]", normalized)) / 300)
    locator_terms = sum(1 for term in ("अध्याय", "श्लोक", "Gita", "Upanishad", "Vedanta", "Mahabharata", "Ramayana") if term.lower() in normalized.lower())
    locator_score = min(1.0, locator_terms / 3)
    spam_terms = sum(1 for term in ("casino", "betting", "crypto bonus", "download now", "viagra") if term in normalized.lower())
    spam_penalty = min(0.4, spam_terms * 0.1)
    rights_bonus = 0.15 if rights_status.upper() in TRAIN_ALLOWED_RIGHTS else 0.0
    robots_penalty = 0.35 if robots_status.upper() == "DISALLOWED" else 0.0
    host_score = 0.1 if parsed.netloc else 0.0
    score = max(0.0, min(1.0, 0.35 * length_score + 0.2 * devanagari_score + 0.2 * locator_score + host_score + rights_bonus - spam_penalty - robots_penalty))
    verdict = "APPROVE_FOR_REVIEW" if score >= 0.65 and robots_status.upper() != "DISALLOWED" else "REVIEW_REQUIRED"
    if spam_terms:
        verdict = "REJECT_OR_MANUAL_REVIEW"
    return WebQualityAssessment(
        score=round(score, 4),
        verdict=verdict,
        components={
            "length_score": round(length_score, 4),
            "devanagari_score": round(devanagari_score, 4),
            "locator_score": round(locator_score, 4),
            "spam_terms": spam_terms,
            "rights_bonus": rights_bonus,
            "robots_penalty": robots_penalty,
            "host": parsed.netloc,
        },
        allowed_usage=allowed_usage_for_rights(rights_status),
    )
