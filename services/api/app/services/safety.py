from __future__ import annotations
from dataclasses import dataclass
import re

SANSKRIT_LIKE_RE = re.compile(r"[\u0900-\u097F]{12,}.*(?:॥|।)", re.UNICODE)
FAKE_CERTAINTY_RE = re.compile(r"(निश्चित रूप से|100%|बिना किसी स्रोत|शास्त्रों में बिल्कुल यही)", re.UNICODE)
HARMFUL_RITUAL_RE = re.compile(r"(तांत्रिक प्रयोग|वशीकरण|मारण|हानि पहुँचाने|बलि)", re.UNICODE)


@dataclass(frozen=True)
class SafetyResult:
    allowed: bool
    flags: list[str]
    reason: str | None = None


def evaluate_query_and_answer(question: str, answer: str, *, citations_count: int) -> SafetyResult:
    flags: list[str] = []
    combined = f"{question}\n{answer}"
    if citations_count == 0:
        flags.append("NO_CITATION")
    if SANSKRIT_LIKE_RE.search(answer) and citations_count == 0:
        flags.append("UNVERIFIED_SANSKRIT")
    if FAKE_CERTAINTY_RE.search(combined):
        flags.append("OVERCONFIDENT_UNSOURCED_CLAIM")
    if HARMFUL_RITUAL_RE.search(combined):
        flags.append("RITUAL_SAFETY_REVIEW")
    hard = {"UNVERIFIED_SANSKRIT", "RITUAL_SAFETY_REVIEW"}
    blocked = any(flag in hard for flag in flags)
    return SafetyResult(
        allowed=not blocked,
        flags=flags,
        reason="; ".join(flags) if flags else None,
    )
