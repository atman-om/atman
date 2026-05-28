import asyncio

from services.api.app.core.db import AsyncSessionLocal
from services.api.app.services.demo_canonical_seed import seed_demo_canonical


async def main() -> None:
    async with AsyncSessionLocal() as session:
        result = await seed_demo_canonical(session)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
