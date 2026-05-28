from __future__ import annotations
import asyncio

from services.api.app.core.db import AsyncSessionLocal
from services.api.app.core.config import get_settings
from services.api.app.deps import get_vector_store
from services.api.app.models import Source
from services.api.app.domain.enums import RightsStatus
from services.api.app.services.ingestion import ingest_plaintext_source

DEMO_TEXT = """
भगवद्गीता 2.47 में कर्म पर अधिकार और फलासक्ति से बचने का सिद्धान्त बताया गया है।
कर्मयोग का आशय यह है कि साधक अपने कर्तव्य को समत्व-बुद्धि से करे।
Atman में किसी भी श्लोक या टीका का दावा स्रोत-सत्यापन के बिना production उत्तर में नहीं जाएगा।
"""


async def main() -> None:
    settings = get_settings()
    async with AsyncSessionLocal() as session:
        source = Source(
            source_type="seed_text",
            title="Atman Demo Gita Notes",
            language="hi",
            rights_status=RightsStatus.USER_OWNED.value,
            source_metadata={"locator": "BG.2.47", "edition": "demo"},
        )
        session.add(source)
        await session.commit()
        await session.refresh(source)
        report = await ingest_plaintext_source(
            session,
            source=source,
            text=DEMO_TEXT,
            vector_store=get_vector_store(),
            embedding_dim=settings.embedding_dim,
        )
        print(report)


if __name__ == "__main__":
    asyncio.run(main())
