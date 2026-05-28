from types import SimpleNamespace

from services.api.app.services.source_explorer import build_highlight, chunk_to_payload, source_rights_explanation


def test_build_highlight_finds_query() -> None:
    text = "कर्मयोग गीता का एक प्रमुख विषय है।"
    highlight = build_highlight(text, "गीता")
    assert highlight is not None
    assert "गीता" in highlight


def test_rights_explanation_public_visibility() -> None:
    src = SimpleNamespace(rights_status="PUBLIC_DOMAIN_VERIFIED", ingestion_status="APPROVED_Z2")
    report = source_rights_explanation(src)
    assert report["public_visible"]
    assert report["allowed_uses"]["rag"]


def test_chunk_payload_contains_highlight() -> None:
    chunk = SimpleNamespace(id="c1", source_id="s1", chunk_text="कर्मयोग और ज्ञानयोग", token_count=3, chunk_order=0, citation_locator={"locator": "BG.2.47"}, quality_score=0.9, review_status="APPROVED")
    payload = chunk_to_payload(chunk, query="ज्ञान")
    assert payload["highlight"] is not None
    assert payload["citation_locator"]["locator"] == "BG.2.47"
