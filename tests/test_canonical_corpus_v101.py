from services.api.app.services.canonical_corpus import (
    grade_from_score,
    locator_sort_key,
    normalize_locator,
    render_citations,
    score_claim_against_text,
    source_authority_score,
    zone_transition_allowed,
)


def test_locator_normalization_and_sort_key() -> None:
    assert normalize_locator(" bg - 2 - 47 ") == "BG.2.47"
    assert locator_sort_key("BG.2.47") == "BG.00000002.00000047"


def test_authority_and_claim_scoring() -> None:
    authority = source_authority_score("PRIMARY", "CANDIDATE", 0.9)
    result = score_claim_against_text("कर्म फल अधिकार", "कर्म करने का अधिकार है फल पर नहीं", authority)
    assert result.support_score > 0.4
    assert result.evidence_grade in {"A", "B", "C", "D"}


def test_citation_visibility_modes() -> None:
    evidence = [{"work_key": "GITA", "title_hi": "भगवद्गीता", "locator": "BG.2.47", "evidence_grade": "A", "text_preview": "x"}]
    assert render_citations(evidence, "hidden") == []
    assert render_citations(evidence, "source")[0]["locator"] == "BG.2.47"
    assert render_citations(evidence, "scholar")[0]["text_preview"] == "x"


def test_zone_transition_rules() -> None:
    assert zone_transition_allowed("Z0_DISCOVERY", "Z1_QUARANTINE") is True
    assert zone_transition_allowed("Z1_QUARANTINE", "Z4_TRAINING_APPROVED") is False
    assert grade_from_score(0.2) == "F"
