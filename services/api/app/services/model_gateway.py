from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from services.api.app.core.config import Settings
from services.api.app.services.qwen_runtime import QwenRuntime


def estimate_tokens(text: str) -> int:
    """Cheap cross-language token estimate for usage dashboards.

    The estimate is intentionally conservative and provider-agnostic; production logs should prefer
    provider-returned usage tokens when available.
    """
    if not text:
        return 0
    devanagari_chars = sum(1 for ch in text if "\u0900" <= ch <= "\u097F")
    ascii_words = len([w for w in text.split() if w.strip()])
    return max(1, int((len(text) - devanagari_chars) / 4) + int(devanagari_chars / 2.2) + ascii_words // 2)


def estimate_cost(settings: Settings, *, input_tokens: int, output_tokens: int) -> float:
    input_cost = (input_tokens / 1000.0) * settings.remote_qwen_cost_per_1k_input_tokens_usd
    output_cost = (output_tokens / 1000.0) * settings.remote_qwen_cost_per_1k_output_tokens_usd
    return round(input_cost + output_cost, 8)


@dataclass(frozen=True)
class ModelRoute:
    feature: str
    provider: str
    model_id: str
    runtime_mode: str
    reason: str


def select_model_route(settings: Settings, feature: str) -> ModelRoute:
    feature_key = feature.lower().strip()
    if feature_key in {"chat", "ask", "rag"}:
        return ModelRoute(feature, settings.remote_qwen_default_provider, settings.qwen_model_id, settings.qwen_runtime_mode, "primary_chat_runtime")
    if feature_key in {"content", "publishing"}:
        return ModelRoute(feature, settings.remote_qwen_default_provider, settings.qwen_model_id, settings.qwen_runtime_mode, "content_generation_runtime")
    if feature_key in {"verify", "eval", "claim_check"}:
        return ModelRoute(feature, settings.remote_qwen_default_provider, settings.qwen_small_model_id, settings.qwen_runtime_mode, "verifier_runtime")
    return ModelRoute(feature, settings.remote_qwen_default_provider, settings.qwen_model_id, settings.qwen_runtime_mode, "default_route")


async def remote_provider_status(settings: Settings) -> dict[str, Any]:
    health = await QwenRuntime(settings).health()
    return {
        "provider": settings.remote_qwen_default_provider,
        "model_id": settings.qwen_model_id,
        "mode": settings.qwen_runtime_mode,
        "base_url_configured": bool(settings.resolved_qwen_base_url),
        "api_key_configured": bool(settings.resolved_qwen_api_key),
        "ready": bool(health.get("ready")),
        "default_for": ["chat", "rag", "content", "source_check"],
        "health": health,
    }
