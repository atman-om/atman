from __future__ import annotations

import asyncio
import httpx


async def main() -> None:
    async with httpx.AsyncClient(timeout=30.0) as client:
        status = await client.get("http://localhost:8000/runtime/status")
        print(status.json())
        response = await client.post(
            "http://localhost:8000/public/ask",
            json={"question": "गीता में कर्मयोग क्या है?", "language": "hi", "top_k": 5},
        )
        response.raise_for_status()
        print(response.json())


if __name__ == "__main__":
    asyncio.run(main())
