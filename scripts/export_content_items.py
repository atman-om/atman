from __future__ import annotations
import argparse
import asyncio
import json

import httpx


async def main() -> None:
    parser = argparse.ArgumentParser(description="Export Atman approved content through the API.")
    parser.add_argument("--api", default="http://localhost:8000")
    parser.add_argument("--format", choices=["jsonl", "markdown", "csv"], default="jsonl")
    parser.add_argument("--batch-id")
    args = parser.parse_args()
    payload = {"export_format": args.format, "batch_id": args.batch_id, "review_status": "APPROVED"}
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(f"{args.api}/content/exports", json=payload)
        response.raise_for_status()
        print(json.dumps(response.json(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
