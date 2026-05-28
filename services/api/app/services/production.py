from __future__ import annotations

from pathlib import Path
from typing import Any

from services.api.app.core.config import Settings


def production_readiness(settings: Settings) -> dict[str, Any]:
    checks: dict[str, Any] = {
        "database_url_configured": bool(settings.database_url),
        "qdrant_url_configured": bool(settings.qdrant_url),
        "redis_url_configured": bool(settings.redis_url),
        "object_store_configured": bool(settings.object_store_endpoint and settings.object_store_bucket),
        "jwt_secret_changed": settings.jwt_secret != "change-me-in-production",
        "qwen_runtime_mode": settings.qwen_runtime_mode,
        "qwen_base_url_configured": bool(settings.resolved_qwen_base_url),
        "network_crawl_enabled": settings.enable_network_crawl,
        "production_auth_required": settings.production_require_auth,
    }
    hard_failures: list[str] = []
    warnings: list[str] = []
    if settings.production_mode and not checks["jwt_secret_changed"]:
        hard_failures.append("jwt_secret_default")
    if settings.production_mode and settings.readiness_require_qwen_when_production and not checks["qwen_base_url_configured"]:
        hard_failures.append("qwen_runtime_not_configured")
    if settings.production_mode and not settings.production_require_auth:
        hard_failures.append("production_auth_disabled")
    if settings.production_mode and settings.qwen_runtime_mode == "deterministic":
        hard_failures.append("deterministic_runtime_in_production")
    if settings.qwen_runtime_mode == "deterministic":
        warnings.append("deterministic_runtime_active; suitable for scaffold/testing, not final AI quality")
    return {
        "ready": not hard_failures,
        "environment": settings.env,
        "production_mode": settings.production_mode,
        "checks": checks,
        "hard_failures": hard_failures,
        "warnings": warnings,
    }


def simulate_backup_manifest(settings: Settings, backup_type: str = "metadata") -> dict[str, Any]:
    root = Path(settings.backup_dir)
    root.mkdir(parents=True, exist_ok=True)
    return {
        "backup_type": backup_type,
        "targets": ["postgres", "qdrant", "minio", "schemas", "prompts"],
        "artifact_uri": str(root / f"atman-{backup_type}-backup-manifest.json"),
        "rpo_minutes": 60,
        "rto_minutes": 120,
        "simulated": True,
    }
