from __future__ import annotations

import asyncio

from services.api.app.core.config import get_settings
from services.api.app.services.qwen_runtime import QwenRuntime


async def main() -> None:
    runtime = QwenRuntime(get_settings())
    print(await runtime.health())
    result = await runtime.generate([{"role": "user", "content": "कर्मयोग क्या है?"}])
    print(result.text)
    print({"provider": result.provider, "latency_ms": result.latency_ms, "warnings": result.warnings})


if __name__ == "__main__":
    asyncio.run(main())
