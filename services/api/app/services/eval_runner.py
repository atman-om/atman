from __future__ import annotations
import json
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.app.models import EvalRun

ROOT = Path(__file__).resolve().parents[4]
DEFAULT_EVAL_DIR = ROOT / "datasets" / "eval"


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


async def run_seed_eval(session: AsyncSession, *, model_version: str, benchmark_name: str) -> EvalRun:
    files = sorted(DEFAULT_EVAL_DIR.glob("nyayabench_*_seed.jsonl"))
    cases = [case for path in files for case in load_jsonl(path)]
    hard_failures = []
    for case in cases:
        if case.get("severity") == "hard_fail" and "blocked_behaviors" not in case:
            hard_failures.append({"case_id": case.get("case_id"), "reason": "missing blocked_behaviors"})
    total = len(cases)
    score = {
        "cases": total,
        "hard_failure_count": len(hard_failures),
        "schema_pass_rate": 1.0 if total and not hard_failures else (0.0 if total else 0.0),
        "note": "v0.3 seed eval checks dataset integrity; model-judged eval is introduced after Qwen service integration.",
    }
    run = EvalRun(
        model_version=model_version,
        benchmark_name=benchmark_name,
        score=score,
        hard_failures=hard_failures,
        approved=total > 0 and len(hard_failures) == 0,
    )
    session.add(run)
    await session.commit()
    await session.refresh(run)
    return run
