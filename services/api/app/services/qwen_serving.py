from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from services.api.app.core.config import Settings


@dataclass(frozen=True)
class QwenServingProfile:
    name: str
    mode: str
    model_id: str
    command: str
    endpoint: str | None
    notes: list[str]


def recommended_profiles(settings: Settings) -> list[QwenServingProfile]:
    return [
        QwenServingProfile(
            name="deterministic-dev",
            mode="deterministic",
            model_id=settings.qwen_model_id,
            command="ATMAN_QWEN_RUNTIME_MODE=deterministic docker compose up --build",
            endpoint=None,
            notes=["No model weights required", "For API/UI smoke tests only", "Not a real LLM"],
        ),
        QwenServingProfile(
            name="gemini-api",
            mode="gemini",
            model_id=settings.gemini_model_id,
            command="ATMAN_QWEN_RUNTIME_MODE=gemini ATMAN_GEMINI_API_KEY=... uvicorn services.api.app.main:app",
            endpoint=settings.gemini_base_url.rstrip("/") + "/chat/completions",
            notes=["Fast path for production chat", "Uses Gemini OpenAI-compatible endpoint", "No Qwen weights required"],
        ),
        QwenServingProfile(
            name="vllm-qwen14b",
            mode="openai_compatible",
            model_id=settings.qwen_model_id,
            command="docker compose -f docker-compose.yml -f docker-compose.qwen.yml --profile qwen-vllm up --build",
            endpoint="http://localhost:8001/v1/chat/completions",
            notes=["GPU recommended", "OpenAI-compatible endpoint", "Set ATMAN_QWEN_BASE_URL=http://qwen-vllm:8000/v1"],
        ),
        QwenServingProfile(
            name="ollama-qwen14b",
            mode="openai_compatible",
            model_id=settings.qwen_ollama_model,
            command="docker compose -f docker-compose.yml -f docker-compose.qwen.yml --profile qwen-ollama up --build",
            endpoint="http://localhost:11434/v1/chat/completions",
            notes=["Simpler local setup", "Pulls Ollama model separately", "Set ATMAN_QWEN_BASE_URL=http://qwen-ollama:11434/v1"],
        ),
    ]


async def check_openai_compatible_health(base_url: str | None, api_key: str | None, timeout: float) -> dict[str, Any]:
    if not base_url:
        return {"reachable": False, "reason": "ATMAN_QWEN_BASE_URL is not configured"}
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    url = base_url.rstrip("/") + "/models"
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url, headers=headers)
        return {
            "reachable": response.status_code < 500,
            "status_code": response.status_code,
            "url": url,
            "preview": response.text[:500],
        }
    except httpx.HTTPError as exc:
        return {"reachable": False, "url": url, "error": str(exc)}


def serving_env(settings: Settings) -> dict[str, Any]:
    return {
        "runtime_mode": settings.qwen_runtime_mode,
        "serving_profile": settings.qwen_serving_profile,
        "model_id": settings.qwen_model_id,
        "small_model_id": settings.qwen_small_model_id,
        "gemini_model_id": settings.gemini_model_id,
        "gemini_base_url": settings.gemini_base_url,
        "gemini_api_key_configured": bool(settings.resolved_gemini_api_key),
        "ollama_model": settings.qwen_ollama_model,
        "base_url": settings.resolved_qwen_base_url,
        "api_key_configured": bool(settings.resolved_qwen_api_key),
        "model_cache_dir": settings.qwen_model_cache_dir,
        "gpu_required": settings.qwen_gpu_required,
    }
