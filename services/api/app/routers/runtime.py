from __future__ import annotations

from fastapi import APIRouter

from services.api.app.core.config import get_settings
from services.api.app.schemas import QwenChatRequest, QwenChatResponse, QwenRuntimeStatus
from services.api.app.services.qwen_runtime import QwenRuntime

router = APIRouter(prefix="/runtime", tags=["qwen-runtime"])


@router.get("/status", response_model=QwenRuntimeStatus)
async def runtime_status() -> QwenRuntimeStatus:
    status = await QwenRuntime(get_settings()).health()
    return QwenRuntimeStatus(**status)


@router.post("/qwen/chat", response_model=QwenChatResponse)
async def qwen_chat(payload: QwenChatRequest) -> QwenChatResponse:
    result = await QwenRuntime(get_settings()).generate(
        payload.messages,
        temperature=payload.temperature,
        max_tokens=payload.max_tokens,
    )
    return QwenChatResponse(
        text=result.text,
        model_name=result.model_name,
        provider=result.provider,
        latency_ms=result.latency_ms,
        usage=result.usage,
        warnings=result.warnings,
    )
