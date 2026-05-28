#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import os
import httpx


async def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test OpenAI-compatible Qwen endpoint.")
    parser.add_argument("--base-url", default=os.getenv("ATMAN_QWEN_BASE_URL", "http://localhost:8001/v1"))
    parser.add_argument("--model", default=os.getenv("ATMAN_QWEN_MODEL_ID", "Qwen/Qwen3-14B"))
    parser.add_argument("--prompt", default="कर्म योग को एक वाक्य में समझाओ।")
    args = parser.parse_args()
    payload = {"model": args.model, "messages": [{"role": "user", "content": args.prompt}], "temperature": 0.2, "max_tokens": 128}
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(args.base_url.rstrip("/") + "/chat/completions", json=payload)
        response.raise_for_status()
        print(response.text[:2000])
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
