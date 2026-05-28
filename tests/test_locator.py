from services.api.app.services.locator import validate_locator, chunk_locator


def test_valid_locator() -> None:
    result = validate_locator("BG.2.47")
    assert result.valid


def test_invalid_locator() -> None:
    result = validate_locator("bg 2 47")
    assert not result.valid


def test_chunk_locator_payload() -> None:
    payload = chunk_locator("BG.2.47", 3)
    assert payload["valid"] is True
    assert payload["chunk_order"] == 3
