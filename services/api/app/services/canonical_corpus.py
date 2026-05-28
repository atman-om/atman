from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Any, Iterable

TOKEN_RE = re.compile(r"[\w\u0900-\u097F]+", re.UNICODE)

AUTHORITY_WEIGHTS = {
    "PRIMARY": 1.00,
    "COMMENTARY": 0.86,
    "TRANSLATION": 0.72,
    "SECONDARY": 0.45,
    "DISCOVERY": 0.20,
}

STATUS_WEIGHTS = {
    "VERIFIED": 1.00,
    "APPROVED": 0.92,
    "CANDIDATE": 0.72,
    "REVIEW_PENDING": 0.48,
    "QUARANTINED": 0.25,
    "REJECTED": 0.00,
}

VISIBLE_CITATION_MODES = {"hidden", "source", "scholar"}


@dataclass(frozen=True)
class EvidenceScore:
    support_score: float
    evidence_grade: str
    matched_terms: list[str]
    missing_terms: list[str]


def normalize_locator(locator: str) -> str:
    """Normalize a source locator while preserving canonical dotted address semantics."""
    cleaned = re.sub(r"\s+", "", locator.strip().upper())
    cleaned = cleaned.replace("-", ".").replace("_", "_")
    cleaned = re.sub(r"\.{2,}", ".", cleaned).strip(".")
    if not cleaned:
        raise ValueError("locator cannot be empty")
    return cleaned


def locator_sort_key(locator: str) -> str:
    normalized = normalize_locator(locator)
    parts: list[str] = []
    for part in normalized.split("."):
        if part.isdigit():
            parts.append(part.zfill(8))
        else:
            parts.append(part)
    return ".".join(parts)


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def tokenize(text: str) -> set[str]:
    return {token.lower() for token in TOKEN_RE.findall(text) if len(token) > 1}


def source_authority_score(authority_level: str, review_status: str, confidence: float) -> float:
    authority = AUTHORITY_WEIGHTS.get(authority_level.upper(), 0.35)
    status = STATUS_WEIGHTS.get(review_status.upper(), 0.40)
    conf = max(0.0, min(1.0, confidence))
    return round(authority * 0.45 + status * 0.35 + conf * 0.20, 4)


def grade_from_score(score: float) -> str:
    if score >= 0.86:
        return "A"
    if score >= 0.70:
        return "B"
    if score >= 0.55:
        return "C"
    if score >= 0.35:
        return "D"
    return "F"


def score_claim_against_text(claim: str, evidence_text: str, authority_score: float = 0.5) -> EvidenceScore:
    claim_terms = tokenize(claim)
    evidence_terms = tokenize(evidence_text)
    if not claim_terms:
        return EvidenceScore(0.0, "F", [], [])
    matched = sorted(claim_terms & evidence_terms)
    missing = sorted(claim_terms - evidence_terms)
    lexical = len(matched) / len(claim_terms)
    support = round((lexical * 0.72) + (max(0.0, min(1.0, authority_score)) * 0.28), 4)
    return EvidenceScore(support, grade_from_score(support), matched, missing)


def render_citations(evidence: list[dict[str, Any]], citation_mode: str) -> list[dict[str, Any]]:
    if citation_mode not in VISIBLE_CITATION_MODES:
        raise ValueError(f"invalid citation_mode={citation_mode!r}")
    if citation_mode == "hidden":
        return []
    if citation_mode == "source":
        return [
            {
                "work_key": item.get("work_key"),
                "title": item.get("title_hi") or item.get("title_en") or item.get("work_key"),
                "locator": item.get("locator"),
                "evidence_grade": item.get("evidence_grade"),
            }
            for item in evidence
        ]
    return evidence


def build_internal_evidence_record(
    *,
    passage_id: str,
    work_key: str,
    title_hi: str | None,
    title_en: str | None,
    locator: str,
    support: EvidenceScore,
    preview: str,
) -> dict[str, Any]:
    return {
        "passage_id": passage_id,
        "work_key": work_key,
        "title_hi": title_hi,
        "title_en": title_en,
        "locator": locator,
        "support_score": support.support_score,
        "evidence_grade": support.evidence_grade,
        "matched_terms": support.matched_terms,
        "missing_terms": support.missing_terms[:20],
        "text_preview": preview[:500],
    }


def zone_transition_allowed(from_zone: str, to_zone: str) -> bool:
    order = ["Z0_DISCOVERY", "Z1_QUARANTINE", "Z2_CANDIDATE_CANONICAL", "Z3_VERIFIED_CANONICAL", "Z4_TRAINING_APPROVED"]
    if from_zone not in order or to_zone not in order:
        return False
    return order.index(to_zone) <= order.index(from_zone) + 1 or to_zone == "Z1_QUARANTINE"


def summarize_manifest_counts(manifest: dict[str, Any]) -> dict[str, int]:
    return {
        "works": len(manifest.get("works", [])),
        "editions": len(manifest.get("editions", [])),
        "passages": len(manifest.get("passages", [])),
    }
