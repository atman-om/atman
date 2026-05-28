from __future__ import annotations
import asyncio
import json
import logging

from redis.asyncio import Redis
from sqlalchemy import select

from services.api.app.core.config import get_settings
from services.api.app.core.db import AsyncSessionLocal
from services.api.app.deps import get_vector_store
from services.api.app.models import ContentBatch
from services.api.app.services.content_factory import run_content_batch

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("atman.worker")


async def handle_job(job: dict) -> None:
    job_type = job.get("type")
    if job_type == "ping":
        log.info("worker ping job acknowledged: %s", job)
        return
    if job_type == "content_batch.run":
        batch_id = job.get("batch_id")
        if not batch_id:
            log.warning("content_batch.run missing batch_id")
            return
        async with AsyncSessionLocal() as session:
            batch = await session.get(ContentBatch, batch_id)
            if batch is None:
                log.warning("content batch not found: %s", batch_id)
                return
            await run_content_batch(session, batch=batch, settings=get_settings(), vector_store=get_vector_store())
            log.info("content batch completed: %s", batch_id)
        return
    log.warning("unknown job type: %s", job_type)


async def main() -> None:
    settings = get_settings()
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    log.info("Atman worker started")
    while True:
        _, payload = await redis.blpop("atman:jobs", timeout=5) or (None, None)
        if payload is None:
            await asyncio.sleep(0.25)
            continue
        try:
            await handle_job(json.loads(payload))
        except Exception:
            log.exception("job failed")


if __name__ == "__main__":
    asyncio.run(main())
