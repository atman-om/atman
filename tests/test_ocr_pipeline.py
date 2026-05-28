from services.api.app.services.ocr import analyze_document_for_ocr, normalize_ocr_text


def test_text_file_ocr_analysis_extracts_text():
    result = analyze_document_for_ocr("sample.txt", "कर्मण्येवाधिकारस्ते".encode("utf-8"))
    assert result.status == "TEXT_EXTRACTED"
    assert result.text_hash
    assert result.confidence >= 0.7


def test_image_file_requires_real_ocr():
    result = analyze_document_for_ocr("scan.png", b"\\x89PNG")
    assert result.status == "OCR_REQUIRED"
    assert result.text is None
    assert result.warnings


def test_ocr_normalizer_collapses_noise():
    assert normalize_ocr_text("a   b\n\n\n c") == "a b\n\n c"
