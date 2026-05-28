from services.api.app.services.model_lab import compare_candidates, dataset_plan
from services.api.app.core.config import Settings


def test_dataset_plan_blocks_raw_scraped_training() -> None:
    settings = Settings()
    report = dataset_plan(name="x", base_model="Qwen/Qwen3-14B", target_sample_count=100, observed={"verified_qa": 10, "reviewed_content": 0, "failure_corrections": 0, "adversarial": 0}, include_raw_scraped=True, settings=settings)
    assert report["allowed_for_training"] is False
    assert "raw_scraped_data_cannot_enter_training_dataset" in report["blockers"]


def test_model_comparison_keeps_remote_baseline_until_gate_passes() -> None:
    settings = Settings()
    result = compare_candidates([{"id": "c1", "model_name": "weak", "eval_summary": {"score": 0.5, "hard_failures": ["fake_shloka"]}}], settings)
    assert result["decision"] == "keep_remote_qwen_as_production"
    assert result["candidates"][0]["can_replace_baseline"] is False
