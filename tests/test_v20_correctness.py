from services.api.app.services.source_correctness import grade_claim_against_evidence, public_claim_allowed


def test_claim_with_primary_evidence_gets_allow_grade() -> None:
    report = grade_claim_against_evidence("गीता में कर्म पर अधिकार बताया गया है", [{"text": "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन", "authority_level": "A", "locator": "BG.2.47"}])
    assert report["support_grade"] in {"A", "B", "C"}
    assert report["verdict"] != "BLOCK"


def test_unsupported_claim_blocks_public_answer() -> None:
    report = grade_claim_against_evidence("यह दावा स्रोत में नहीं है", [])
    assert report["support_grade"] == "F"
    assert public_claim_allowed(report["support_grade"], "B") is False
