from __future__ import annotations

from typing import Any

from services.api.app.core.config import Settings

DEFAULT_MIX = {"verified_qa": 0.45, "reviewed_content": 0.25, "failure_corrections": 0.20, "adversarial": 0.10}


def dataset_plan(*, name: str, base_model: str, target_sample_count: int, observed: dict[str, int], include_raw_scraped: bool, settings: Settings) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    if include_raw_scraped:
        blockers.append("raw_scraped_data_cannot_enter_training_dataset")
    verified_total = observed.get("verified_qa", 0) + observed.get("reviewed_content", 0)
    if verified_total < settings.model_lab_min_verified_samples:
        warnings.append("verified_sample_count_below_parallel_training_target")
    if observed.get("failure_corrections", 0) < settings.model_lab_min_rejected_samples:
        warnings.append("failure_correction_count_low_for_robust_alignment")
    manifest = {
        "name": name,
        "base_model": base_model,
        "target_sample_count": target_sample_count,
        "sample_policy": {
            "allow_raw_scraped": False,
            "allow_quarantine": False,
            "allow_verified_canonical": True,
            "allow_reviewed_content": True,
            "allow_failure_corrections": True,
        },
        "release_rule": "parallel experiment only; cannot replace production remote Qwen until NyayaBench gate passes",
    }
    return {
        "name": name,
        "base_model": base_model,
        "target_sample_count": target_sample_count,
        "observed_samples": observed,
        "recommended_mix": DEFAULT_MIX,
        "allowed_for_training": not blockers,
        "blockers": blockers,
        "warnings": warnings,
        "manifest": manifest,
    }


def readiness(counts: dict[str, int], settings: Settings) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    verified_samples = counts.get("training_datasets", 0) * 100 + counts.get("canonical_passages", 0)
    failure_cases = counts.get("failure_cases", 0)
    if not settings.enable_model_lab:
        blockers.append("model_lab_disabled")
    if counts.get("canonical_passages", 0) == 0:
        warnings.append("canonical_passage_count_zero")
    if verified_samples < settings.model_lab_min_verified_samples:
        warnings.append("insufficient_verified_training_signal")
    if failure_cases < settings.model_lab_min_rejected_samples:
        warnings.append("insufficient_failure_corrections")
    mode = settings.qwen_runtime_mode.strip().lower()
    score_parts = [
        min(1.0, counts.get("canonical_passages", 0) / max(settings.model_lab_min_verified_samples, 1)),
        min(1.0, counts.get("content_items", 0) / 100),
        min(1.0, max(failure_cases, counts.get("chat_feedback", 0)) / max(settings.model_lab_min_rejected_samples, 1)),
        1.0 if mode in {"openai_compatible", "gemini"} else 0.7,
    ]
    score = round(sum(score_parts) / len(score_parts), 4)
    next_actions = []
    if "canonical_passage_count_zero" in warnings:
        next_actions.append("import Gita/Veda/Upanishad canonical manifests")
    if "insufficient_failure_corrections" in warnings:
        next_actions.append("convert downvoted/wrong chatbot feedback into failure cases")
    next_actions.append("run simulated LoRA plan before enabling real GPU job")
    return {
        "mode": settings.model_lab_mode,
        "live_app_runtime": "gemini_api" if mode == "gemini" else "remote_qwen_api",
        "fine_tuning_lane": "parallel_r_and_d",
        "production_replacement_allowed": False,
        "counts": counts,
        "readiness_score": score,
        "blockers": blockers,
        "warnings": warnings,
        "next_actions": next_actions,
    }


def default_training_config(settings: Settings) -> dict[str, Any]:
    return {
        "method": settings.training_default_adapter_method,
        "base_model": settings.training_default_base_model,
        "lora_rank": settings.training_lora_rank,
        "lora_alpha": settings.training_lora_alpha,
        "learning_rate": settings.training_learning_rate,
        "epochs": settings.training_epochs,
        "real_jobs_enabled": settings.training_allow_real_jobs,
    }


def compare_candidates(checkpoints: list[dict[str, Any]], settings: Settings) -> dict[str, Any]:
    baseline = {"name": "remote_qwen_api", "role": "production_default", "replaceable": False}
    candidates = []
    for cp in checkpoints:
        summary = cp.get("eval_summary") or {}
        score = float(summary.get("score") or summary.get("overall_score") or 0.0)
        hard_failures = summary.get("hard_failures") or []
        candidates.append({
            "checkpoint_id": cp.get("id"),
            "model_name": cp.get("model_name"),
            "score": score,
            "hard_failures": hard_failures,
            "can_replace_baseline": score >= settings.model_lab_release_gate_score and not hard_failures,
        })
    decision = "keep_remote_qwen_as_production" if not any(c["can_replace_baseline"] for c in candidates) else "candidate_ready_for_staging_gate"
    return {"baseline": baseline, "candidates": candidates, "decision": decision, "release_rule": "Atman-Qwen adapter replaces remote baseline only after NyayaBench, citation, fake-shloka, and human approval gates."}
