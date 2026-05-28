from services.api.app.core.config import Settings
from services.api.app.services.production import production_readiness, simulate_backup_manifest


def test_local_readiness_warns_deterministic_runtime_but_allows_scaffold():
    settings = Settings(jwt_secret="dev-secret", qwen_runtime_mode="deterministic")
    report = production_readiness(settings)
    assert report["ready"] is True
    assert any("deterministic" in warning for warning in report["warnings"])


def test_production_readiness_blocks_default_secret():
    settings = Settings(production_mode=True, jwt_secret="change-me-in-production")
    report = production_readiness(settings)
    assert report["ready"] is False
    assert "jwt_secret_default" in report["hard_failures"]


def test_production_readiness_blocks_disabled_auth_even_with_rotated_secret():
    settings = Settings(
        production_mode=True,
        jwt_secret="rotated-secret",
        qwen_runtime_mode="openai_compatible",
        qwen_base_url="http://qwen.local/v1",
        production_require_auth=False,
    )
    report = production_readiness(settings)
    assert report["ready"] is False
    assert "production_auth_disabled" in report["hard_failures"]


def test_production_readiness_blocks_deterministic_runtime_in_production():
    settings = Settings(
        production_mode=True,
        production_require_auth=True,
        jwt_secret="rotated-secret",
        qwen_base_url="http://qwen.local/v1",
        qwen_runtime_mode="deterministic",
    )
    report = production_readiness(settings)
    assert report["ready"] is False
    assert "deterministic_runtime_in_production" in report["hard_failures"]


def test_backup_manifest_shape(tmp_path):
    settings = Settings(backup_dir=str(tmp_path))
    manifest = simulate_backup_manifest(settings)
    assert manifest["simulated"] is True
    assert "postgres" in manifest["targets"]
