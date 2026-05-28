from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.api.app.services.training import build_training_dataset

samples = [json.loads(line) for line in Path("datasets/training/seed_training_samples.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
report = build_training_dataset(samples, name="atman_seed_training", base_model="Qwen/Qwen3-14B")
print(json.dumps(report.manifest, ensure_ascii=False, indent=2))
