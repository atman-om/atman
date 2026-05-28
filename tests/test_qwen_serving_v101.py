from services.api.app.core.config import Settings
from services.api.app.services.qwen_serving import recommended_profiles, serving_env


def test_recommended_profiles_include_real_serving_options() -> None:
    settings = Settings()
    profiles = recommended_profiles(settings)
    names = {profile.name for profile in profiles}
    assert "deterministic-dev" in names
    assert "vllm-qwen14b" in names
    assert "ollama-qwen14b" in names


def test_serving_env_declares_weights_external() -> None:
    settings = Settings(qwen_base_url="http://localhost:8001/v1")
    env = serving_env(settings)
    assert env["model_id"].startswith("Qwen/")
    assert env["base_url"] == "http://localhost:8001/v1"
