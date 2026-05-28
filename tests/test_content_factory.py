from services.api.app.schemas import ContentGenerateRequest
from services.api.app.services.content_logic import build_content_body, evaluate_content_quality
from types import SimpleNamespace


def test_quality_blocks_missing_required_source() -> None:
    report = evaluate_content_quality(body="यह एक छोटा उत्तर है", source_chunk_ids=[], source_required=True, quantity=5)
    assert "SOURCE_REQUIRED_BUT_MISSING" in report["flags"]
    assert report["recommended_review_status"] == "AUTO_BLOCKED"


def test_quality_passes_with_source_chunks() -> None:
    body = "स्रोत-आधारित व्याख्या। " * 80
    report = evaluate_content_quality(body=body, source_chunk_ids=["c1", "c2", "c3"], source_required=True, quantity=3)
    assert report["score"] > 0.7
    assert report["recommended_review_status"] == "REVIEW_PENDING"


def test_content_body_contains_source_basis() -> None:
    req = ContentGenerateRequest(content_type="notes", topic="कर्मयोग", quantity=1)
    chunks = [SimpleNamespace(chunk_id="c1", locator={"locator":"BG.2.47"}, text="कर्मण्येवाधिकारस्ते...")]
    body = build_content_body(req, "उत्तर", chunks, item_index=1)
    assert "स्रोत-आधार" in body
    assert "BG.2.47" in body
