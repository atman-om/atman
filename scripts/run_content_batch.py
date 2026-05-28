from __future__ import annotations
import argparse
import asyncio
import json

import httpx


async def main() -> None:
    parser = argparse.ArgumentParser(description="Create and run an Atman content batch through the API.")
    parser.add_argument("--api", default="http://localhost:8000")
    parser.add_argument("--topic", default="कर्मयोग")
    parser.add_argument("--content-type", default="notes")
    parser.add_argument("--quantity", type=int, default=5)
    args = parser.parse_args()
    payload = {
        "name": f"CLI batch: {args.topic}",
        "topic": args.topic,
        "content_type": args.content_type,
        "quantity": args.quantity,
        "source_required": True,
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        created = (await client.post(f"{args.api}/content/batches", json=payload)).raise_for_status()
        batch = created.json()
        run = await client.post(f"{args.api}/content/batches/{batch['id']}/run")
        run.raise_for_status()
        print(json.dumps(run.json(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
