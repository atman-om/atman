from types import SimpleNamespace

import pytest

from services.api.app.services.qwen_runtime import QwenRuntime, build_rag_messages


def settings(**overrides):
    base = dict(
        model_family="Qwen",
        runtime_model="Atman-Lab-Qwen-14B-v0.5",
        qwen_runtime_mode="deterministic",
        qwen_model_id="Qwen/Qwen3-14B",
        qwen_temperature=0.2,
        qwen_max_tokens=900,
        qwen_request_timeout_seconds=60.0,
        qwen_enable_transformers_runtime=False,
        resolved_qwen_base_url=None,
        resolved_qwen_api_key=None,
        gemini_base_url="https://generativelanguage.googleapis.com/v1beta/openai",
        gemini_model_id="gemini-2.5-flash",
        resolved_gemini_api_key=None,
    )
    base.update(overrides)
    return SimpleNamespace(**base)


@pytest.mark.asyncio
async def test_qwen_deterministic_runtime_returns_trace() -> None:
    runtime = QwenRuntime(settings())
    result = await runtime.generate([{"role": "user", "content": "कर्मयोग क्या है?"}])
    assert result.provider == "qwen_deterministic_fallback"
    assert "trace_id" in result.text
    assert result.model_name == "Atman-Lab-Qwen-14B-v0.5"


@pytest.mark.asyncio
async def test_gemini_runtime_health_uses_gemini_key() -> None:
    runtime = QwenRuntime(settings(qwen_runtime_mode="gemini", resolved_gemini_api_key="key"))
    health = await runtime.health()
    assert health["provider"] == "gemini_openai_compatible"
    assert health["ready"] is True
    assert health["api_key_configured"] is True
    assert health["gemini_model_id"] == "gemini-2.5-flash"


@pytest.mark.asyncio
async def test_gemini_runtime_falls_back_without_api_key() -> None:
    runtime = QwenRuntime(settings(qwen_runtime_mode="gemini"))
    result = await runtime.generate([{"role": "user", "content": "test"}])
    assert result.provider == "qwen_deterministic_fallback_after_error"
    assert result.model_name == "gemini-2.5-flash"
    assert any("ATMAN_GEMINI_API_KEY" in warning for warning in result.warnings)


def test_build_rag_messages_includes_source_blocks() -> None:
    messages = build_rag_messages(
        question="कर्मयोग?",
        source_blocks=[{"title": "Gita", "locator": {"locator": "BG.2.47"}, "text": "कर्मण्येवाधिकारस्ते"}],
    )
    joined = "\n".join(m.content for m in messages)
    assert "[SOURCE:1]" in joined
    assert "BG.2.47" in joined
