from services.api.app.schemas import PublicAskRequest, QwenChatRequest


def test_public_ask_schema_defaults() -> None:
    req = PublicAskRequest(question="कर्मयोग क्या है?")
    assert req.language == "hi"
    assert req.top_k == 5
    assert req.mode == "simple"


def test_qwen_chat_schema() -> None:
    req = QwenChatRequest(messages=[{"role": "user", "content": "hi"}])
    assert req.messages[0]["role"] == "user"
