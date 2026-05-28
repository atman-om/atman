from services.api.app.services.modelops import evaluate_model_release_gate
from services.api.app.services.training import build_training_dataset, normalize_training_sample, qlora_config, simulate_training_metrics


def test_training_sample_rejects_no_training_rights():
    sample, error = normalize_training_sample({"prompt": "Q", "completion": "A", "rights_status": "NO_TRAINING_ALLOWED"})
    assert sample is None
    assert "rights_not_trainable" in error


def test_training_dataset_manifest_tracks_rejections():
    report = build_training_dataset([
        {"prompt": "कर्म क्या है?", "completion": "स्रोत आधारित उत्तर", "rights_status": "PUBLIC_DOMAIN_VERIFIED"},
        {"prompt": "bad", "completion": "bad", "rights_status": "REFERENCE_ONLY"},
    ], name="seed", base_model="Qwen/Qwen3-14B")
    assert report.sample_count == 1
    assert report.rejected_count == 1
    assert report.manifest["sha256"]


def test_qlora_config_uses_qwen_targets():
    cfg = qlora_config(base_model="Qwen/Qwen3-14B")
    assert cfg["method"] == "qlora"
    assert "q_proj" in cfg["target_modules"]


def test_simulated_metrics_scale_with_samples():
    assert simulate_training_metrics(5000)["citation_obedience_probe"] >= simulate_training_metrics(10)["citation_obedience_probe"]


def test_model_release_gate_blocks_low_score():
    gate = evaluate_model_release_gate({"score": 0.4, "hard_failures": []}, min_score=0.92, require_no_hard_failures=True)
    assert gate.allowed is False
    assert gate.gate_report["decision"] == "BLOCK"


def test_model_release_gate_allows_clean_checkpoint():
    gate = evaluate_model_release_gate({"score": 0.96, "hard_failures": []}, min_score=0.92, require_no_hard_failures=True)
    assert gate.allowed is True
