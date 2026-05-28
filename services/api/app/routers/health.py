from fastapi import APIRouter
from services.api.app.core.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, object]:
    settings = get_settings()
    return {
        "status": "ok",
        "env": settings.env,
        "model_family": settings.model_family,
        "runtime_model": settings.runtime_model,
        "content_model": settings.content_model,
        "content_export_dir": settings.content_export_dir,
        "qwen_runtime_mode": settings.qwen_runtime_mode,
        "qwen_model_id": settings.qwen_model_id,
        "public_app_name": settings.public_app_name,
        "upload_dir": settings.upload_dir,
        "max_upload_bytes": settings.max_upload_bytes,
    }
