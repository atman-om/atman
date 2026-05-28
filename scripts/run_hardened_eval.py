from __future__ import annotations

import asyncio
import json

from services.api.app.core.db import AsyncSessionLocal
from services.api.app.services.eval_hardening import run_hardened_eval


async def main() -> None:
    async with AsyncSessionLocal() as session:
        run, _results, category_scores, release_readiness = await run_hardened_eval(
            session,
            model_version="Atman-Lab-Qwen-14B-v0.7",
            benchmark_name="nyayabench_hardened",
            dataset_glob="nyayabench_*_seed.jsonl",
            persist_cases=True,
        )
        print(json.dumps({
            "run_id": run.id,
            "approved": run.approved,
            "score": run.score,
            "category_scores": category_scores,
            "release_readiness": release_readiness,
        }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
