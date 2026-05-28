from __future__ import annotations

import re
from typing import Any

GRADE_ORDER = {"A": 5, "B": 4, "C": 3, "D": 2, "F": 1}


def _normalize(text: str) -> set[str]:
    return {tok for tok in re.findall(r"[\wऀ-ॿ]+", text.lower()) if len(tok) > 2}


def grade_claim_against_evidence(claim: str, evidence: list[dict[str, Any]], strictness: str = "normal") -> dict[str, Any]:
    claim_terms = _normalize(claim)
    warnings: list[str] = []
    if not claim_terms:
        return {"support_grade": "F", "confidence": 0.0, "verdict": "BLOCK", "warnings": ["empty_or_unusable_claim"], "evidence": []}
    scored: list[dict[str, Any]] = []
    best = 0.0
    for item in evidence:
        text = str(item.get("text") or item.get("text_preview") or item.get("passage") or item.get("normalized_text") or "")
        terms = _normalize(text)
        exact_hits = len(claim_terms & terms)
        partial_hits = 0
        lowered = text.lower()
        for term in claim_terms - terms:
            if len(term) >= 4 and (term in lowered or term[:4] in lowered):
                partial_hits += 1
        overlap = min(1.0, (exact_hits + 0.65 * partial_hits) / max(len(claim_terms), 1))
        authority = str(item.get("authority_level") or item.get("evidence_grade") or "C").upper()[:1]
        authority_bonus = {"A": 0.25, "B": 0.18, "C": 0.08}.get(authority, 0.0)
        score = min(1.0, overlap + authority_bonus)
        if authority == "A" and item.get("locator") and text.strip():
            score = max(score, 0.50)
        best = max(best, score)
        enriched = dict(item)
        enriched["support_score"] = round(score, 4)
        enriched["term_overlap"] = round(overlap, 4)
        scored.append(enriched)
    strict_delta = {"loose": -0.08, "normal": 0.0, "strict": 0.08}.get(strictness, 0.0)
    if best >= 0.82 + strict_delta:
        grade, verdict = "A", "ALLOW"
    elif best >= 0.65 + strict_delta:
        grade, verdict = "B", "ALLOW"
    elif best >= 0.45 + strict_delta:
        grade, verdict = "C", "LABEL_SECONDARY_OR_REVIEW"
    elif best >= 0.22 + strict_delta:
        grade, verdict = "D", "REVIEW_REQUIRED"
    else:
        grade, verdict = "F", "BLOCK"
    if not evidence:
        warnings.append("no_evidence_supplied")
    if grade in {"D", "F"}:
        warnings.append("claim_not_sufficiently_supported")
    return {"support_grade": grade, "confidence": round(best, 4), "verdict": verdict, "warnings": warnings, "evidence": scored}


def public_claim_allowed(grade: str, min_grade: str = "B") -> bool:
    return GRADE_ORDER.get(grade, 0) >= GRADE_ORDER.get(min_grade, 4)
