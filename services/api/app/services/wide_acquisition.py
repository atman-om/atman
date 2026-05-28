from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from services.api.app.services.hashutil import sha256_text


@dataclass(frozen=True)
class AcquisitionAssessment:
    quality_score: float
    zone: str
    status: str
    report: dict[str, Any]


def assess_acquisition_candidate(*, uri: str, text: str | None, rights_signal: str, mode: str) -> AcquisitionAssessment:
    text = text or ""
    length_score = min(len(text) / 5000.0, 1.0) if text else 0.10
    dharma_terms = ["veda", "gita", "upanishad", "ramayana", "mahabharata", "पुराण", "गीता", "वेद", "उपनिषद"]
    term_hits = sum(1 for term in dharma_terms if term.lower() in (uri + " " + text).lower())
    relevance_score = min(term_hits / 3.0, 1.0)
    rights_bonus = 0.2 if rights_signal.upper() in {"PUBLIC_DOMAIN_VERIFIED", "OPEN_LICENSE_VERIFIED", "USER_OWNED"} else 0.0
    quality = round(min(1.0, (length_score * 0.45) + (relevance_score * 0.35) + rights_bonus), 4)
    zone = "Z1_QUARANTINE"
    status = "QUARANTINED"
    if quality >= 0.75 and rights_bonus > 0:
        zone = "Z2_CANDIDATE_CANONICAL"
        status = "CANDIDATE_READY"
    return AcquisitionAssessment(
        quality_score=quality,
        zone=zone,
        status=status,
        report={
            "uri": uri,
            "mode": mode,
            "text_hash": sha256_text(text) if text else None,
            "length_score": round(length_score, 4),
            "relevance_score": round(relevance_score, 4),
            "rights_signal": rights_signal,
            "decision": "store_in_quarantine_first",
        },
    )
