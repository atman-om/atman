from services.api.app.services.embedding import deterministic_embedding, cosine


def test_embedding_is_deterministic_and_normalized() -> None:
    a = deterministic_embedding("कर्म योग", dim=64)
    b = deterministic_embedding("कर्म योग", dim=64)
    assert a == b
    assert len(a) == 64
    assert cosine(a, b) > 0.999
