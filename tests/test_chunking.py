from services.api.app.services.chunking import chunk_text, count_tokens, normalize_text


def test_normalize_text_compacts_whitespace() -> None:
    assert normalize_text("a   b\n\n\n c") == "a b\n\n c"


def test_chunk_text_respects_max_tokens() -> None:
    text = " ".join(f"word{i}." for i in range(120))
    chunks = chunk_text(text, max_tokens=30, overlap_tokens=5)
    assert chunks
    assert all(chunk.token_count <= 30 for chunk in chunks)
    assert chunks[0].order == 0
