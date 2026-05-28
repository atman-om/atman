from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ModelReleaseGate:
    allowed: bool
    gate_report: dict[str, Any]


def evaluate_model_release_gate(
    eval_summary: dict[str, Any],
    *,
    min_score: float,
    require_no_hard_failures: bool,
    required_approvals: list[str] | None = None,
) -> ModelReleaseGate:
    score = float(eval_summary.get("score", eval_summary.get("overall_score", 0.0)) or 0.0)
    hard_failures = eval_summary.get("hard_failures", []) or []
    approvals = required_approvals or []
    failures: list[str] = []
    if score < min_score:
        failures.append(f"score_below_threshold:{score:.4f}<{min_score:.4f}")
    if require_no_hard_failures and hard_failures:
        failures.append(f"hard_failures_present:{len(hard_failures)}")
    if approvals:
        failures.append("manual_approvals_required:" + ",".join(approvals))
    return ModelReleaseGate(
        allowed=not failures,
        gate_report={
            "score": score,
            "min_score": min_score,
            "hard_failure_count": len(hard_failures),
            "required_approvals": approvals,
            "failures": failures,
            "decision": "ALLOW" if not failures else "BLOCK",
        },
    )


def default_serving_profile(model_name: str, endpoint_url: str | None = None) -> dict[str, Any]:
    return {
        "name": "prod-qwen-runtime",
        "model_name": model_name,
        "runtime_mode": "openai_compatible" if endpoint_url else "deterministic",
        "endpoint_url": endpoint_url,
        "config": {
            "temperature": 0.2,
            "max_tokens": 900,
            "source_required": True,
            "streaming": True,
            "fallback": "deterministic",
        },
    }
