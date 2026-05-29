from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from services.api.app.core.config import get_settings
from services.api.app.services.qwen_serving import check_openai_compatible_health, recommended_profiles, serving_env
from services.api.app.services.qwen_runtime import QwenRuntime

router = APIRouter(prefix="/qwen/serving", tags=["qwen-serving-v1.0.1"])


class SmokeRequest(BaseModel):
    prompt: str = Field(default="कर्म योग को एक वाक्य में समझाओ।", min_length=2, max_length=1000)


@router.get("/profiles")
async def profiles() -> list[dict[str, Any]]:
    settings = get_settings()
    return [profile.__dict__ for profile in recommended_profiles(settings)]


@router.get("/status")
async def status() -> dict[str, Any]:
    settings = get_settings()
    health = None
    mode = settings.qwen_runtime_mode.strip().lower()
    if mode == "openai_compatible":
        health = await check_openai_compatible_health(
            settings.resolved_qwen_base_url,
            settings.resolved_qwen_api_key,
            settings.qwen_request_timeout_seconds,
        )
    elif mode == "gemini":
        health = await check_openai_compatible_health(
            settings.gemini_base_url,
            settings.resolved_gemini_api_key,
            settings.qwen_request_timeout_seconds,
        )
    return {
        "serving": serving_env(settings),
        "remote_health": health,
        "weights_bundled": False,
        "message": "Repo contains Qwen serving profiles/connectors; model weights are external.",
    }


@router.post("/smoke-test")
async def smoke_test(payload: SmokeRequest) -> dict[str, Any]:
    settings = get_settings()
    runtime = QwenRuntime(settings)
    result = await runtime.generate(messages=[{"role": "user", "content": payload.prompt}])
    return {
        "mode": settings.qwen_runtime_mode,
        "model_id": result.model_name,
        "provider": result.provider,
        "response": result.text,
        "usage": result.usage,
        "warnings": result.warnings,
    }
