from __future__ import annotations

from fastapi import APIRouter

from services.api.app.core.config import get_settings
from services.api.app.schemas import KnowledgeOSStatusOut
from services.api.app.services.knowledge_os import capability_map, status

router = APIRouter(prefix="/os", tags=["knowledge-os-v2.0"])


@router.get("/status", response_model=KnowledgeOSStatusOut)
async def get_status() -> KnowledgeOSStatusOut:
    return KnowledgeOSStatusOut(**status(get_settings()))


@router.get("/capabilities")
async def get_capabilities() -> dict[str, object]:
    settings = get_settings()
    return {"version": settings.product_version, "capabilities": capability_map(settings)}


@router.get("/launch-plan")
async def launch_plan() -> dict[str, object]:
    return {
        "live_lane": ["remote_qwen_chatbot", "canonical_corpus_rag", "public_app", "content_studio"],
        "parallel_lane": ["dataset_builder", "model_lab_experiments", "qwen_lora_plans", "nyayabench_gate"],
        "rule": "fine_tuning_runs_in_parallel_but_does_not_block_live_app",
    }
