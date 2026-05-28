from services.api.app.core.config import Settings
from services.api.app.services.knowledge_os import status


def test_v20_status_declares_parallel_model_lab() -> None:
    data = status(Settings())
    assert data["version"] == "2.0.0"
    assert data["parallel_model_lab"] is True
    assert "model_lab" in data["capability_map"]
