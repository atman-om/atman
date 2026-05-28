from __future__ import annotations

from typing import Any

from services.api.app.core.config import Settings


def launch_surfaces(settings: Settings) -> list[str]:
    return [part.strip() for part in settings.os_launch_surface.split(',') if part.strip()]


def capability_map(settings: Settings) -> dict[str, Any]:
    return {
        "chatbot": {"status": "active", "runtime": settings.qwen_runtime_mode, "citation_modes": ["hidden", "source", "scholar"]},
        "canonical_library": {"status": "active", "zones": ["Z0_DISCOVERY", "Z1_QUARANTINE", "Z2_CANDIDATE", "Z3_VERIFIED", "Z4_TRAINING_APPROVED"]},
        "content_studio": {"status": "active", "exports": ["jsonl", "markdown", "csv"], "publishing": True},
        "learning": {"status": "active" if settings.learning_enable_paths else "disabled", "default_language": settings.learning_default_language},
        "model_lab": {"status": "parallel" if settings.enable_model_lab else "disabled", "base_model": settings.training_default_base_model},
        "analytics": {"status": "active", "cost_currency": settings.billing_currency},
    }


def status(settings: Settings) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    if settings.qwen_runtime_mode == "openai_compatible" and not settings.resolved_qwen_base_url:
        warnings.append("remote_qwen_base_url_missing")
    if settings.enable_model_lab and settings.training_allow_real_jobs:
        warnings.append("real_training_jobs_enabled_check_gpu_and_dataset_governance")
    return {
        "version": settings.product_version,
        "codename": settings.product_codename,
        "primary_runtime": settings.qwen_runtime_mode,
        "live_brain": "remote_qwen_api" if settings.qwen_runtime_mode == "openai_compatible" else settings.qwen_runtime_mode,
        "parallel_model_lab": settings.enable_model_lab,
        "launch_surfaces": launch_surfaces(settings),
        "capability_map": capability_map(settings),
        "blockers": blockers,
        "warnings": warnings,
    }
