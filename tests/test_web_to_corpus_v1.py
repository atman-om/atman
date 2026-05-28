from services.api.app.services.web_quality import allowed_usage_for_rights, score_web_source_text
from services.api.app.services.web_to_corpus import extract_article_text


def test_web_quality_scores_dharma_source_above_review_threshold():
    text = "भगवद्गीता अध्याय 2 श्लोक 47 कर्मयोग व्याख्या। " * 80
    result = score_web_source_text(text, url="https://example.org/gita", rights_status="PUBLIC_DOMAIN_VERIFIED", robots_status="ALLOWED")
    assert result.score >= 0.65
    assert result.allowed_usage["train"] is True


def test_rights_matrix_blocks_reference_only_training():
    usage = allowed_usage_for_rights("REFERENCE_ONLY")
    assert usage["store"] is True
    assert usage["train"] is False


def test_article_text_extraction_removes_script():
    title, text = extract_article_text("<html><title>T</title><script>x</script><main>धर्म पाठ</main></html>")
    assert title == "T"
    assert "धर्म पाठ" in text
    assert "script" not in text.lower()
