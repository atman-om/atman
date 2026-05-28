from __future__ import annotations
import asyncio

from services.api.app.core.db import AsyncSessionLocal
from services.api.app.services.eval_runner import run_seed_eval


async def main() -> None:
    async with AsyncSessionLocal() as session:
        run = await run_seed_eval(session, model_version="Atman-Lab-Qwen-14B-v0.1", benchmark_name="nyayabench_seed")
        print(run.id, run.score, "approved=", run.approved)


if __name__ == "__main__":
    asyncio.run(main())
