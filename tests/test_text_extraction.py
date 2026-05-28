from services.api.app.services.text_extraction import extract_text_from_bytes, normalize_extracted_text


def test_plain_text_extraction() -> None:
    result = extract_text_from_bytes("demo.txt", "कर्म   योग\n\n\nज्ञान".encode("utf-8"))
    assert result.source_type == "text"
    assert "कर्म योग" in result.text
    assert result.report["text_chars"] > 0


def test_html_extraction_removes_script() -> None:
    html = b"<html><script>bad()</script><body><h1>Gita</h1><p>Karma</p></body></html>"
    result = extract_text_from_bytes("demo.html", html)
    assert "bad" not in result.text
    assert "Gita" in result.text


def test_normalize_extracted_text() -> None:
    assert normalize_extracted_text("a   b\n\n\n c") == "a b\n\n c"
