from __future__ import annotations
import asyncio
import json
from redis.asyncio import Redis
from services.api.app.core.config import get_settings


async def main() -> None:
    redis = Redis.from_url(get_settings().redis_url, decode_responses=True)
    await redis.rpush("atman:jobs", json.dumps({"type": "ping", "source": "script"}))
    print("queued ping")


if __name__ == "__main__":
    asyncio.run(main())
