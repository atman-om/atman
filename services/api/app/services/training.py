from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import hashlib
import json


@dataclass(frozen=True)
class DatasetBuildReport:
    sample_count: int
    rejected_count: int
    manifest: dict[str, Any]
    jsonl: str


def normalize_training_sample(sample: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    prompt = str(sample.get("prompt", "")).strip()
    completion = str(sample.get("completion", "")).strip()
    rights = str(sample.get("rights_status", "UNKNOWN")).upper()
    if not prompt or not completion:
        return None, "missing_prompt_or_completion"
    if rights in {"REFERENCE_ONLY", "NO_TRAINING_ALLOWED", "NO_STORAGE_ALLOWED", "REJECTED", "UNKNOWN"}:
        return None, f"rights_not_trainable:{rights}"
    normalized = {
        "messages": [
            {"role": "system", "content": "तुम Atman हो: स्रोत-आधारित, हिंदी-प्रथम, उद्धरण-अनुशासित सहायक।"},
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": completion},
        ],
        "provenance": {
            "source_ids": list(sample.get("source_ids", [])),
            "chunk_ids": list(sample.get("chunk_ids", [])),
            "rights_status": rights,
            "metadata": dict(sample.get("metadata", {})),
        },
    }
    return normalized, None


def build_training_dataset(samples: list[dict[str, Any]], *, name: str, base_model: str) -> DatasetBuildReport:
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, str]] = []
    for idx, sample in enumerate(samples):
        normalized, error = normalize_training_sample(sample)
        if normalized is None:
            rejected.append({"index": str(idx), "reason": error or "unknown"})
        else:
            accepted.append(normalized)
    jsonl = "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in accepted)
    digest = hashlib.sha256(jsonl.encode("utf-8")).hexdigest()
    manifest = {
        "name": name,
        "base_model": base_model,
        "sample_count": len(accepted),
        "rejected_count": len(rejected),
        "sha256": digest,
        "format": "chatml-jsonl",
        "contamination_policy": "external_llm_output_not_directly_trainable_without_rights_and_review",
        "rejections": rejected[:100],
    }
    return DatasetBuildReport(len(accepted), len(rejected), manifest, jsonl)


def qlora_config(*, base_model: str, rank: int = 64, alpha: int = 128, learning_rate: float = 2e-5, epochs: int = 3) -> dict[str, Any]:
    return {
        "base_model": base_model,
        "method": "qlora",
        "lora_rank": rank,
        "lora_alpha": alpha,
        "learning_rate": learning_rate,
        "epochs": epochs,
        "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        "output_adapter": "generated/training/adapters/atman-qwen-adapter",
    }


def simulate_training_metrics(sample_count: int) -> dict[str, Any]:
    coverage = min(1.0, sample_count / 5000)
    return {
        "simulated": True,
        "sample_count": sample_count,
        "estimated_loss": round(max(0.8, 2.4 - coverage), 4),
        "citation_obedience_probe": round(0.72 + 0.18 * coverage, 4),
        "requires_real_gpu_run": sample_count >= 500,
    }


def write_dataset_artifact(root: str, name: str, report: DatasetBuildReport) -> str:
    safe_name = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in name)[:128]
    out_dir = Path(root) / "datasets"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{safe_name}.jsonl"
    path.write_text(report.jsonl + ("\n" if report.jsonl else ""), encoding="utf-8")
    (out_dir / f"{safe_name}.manifest.json").write_text(json.dumps(report.manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)
