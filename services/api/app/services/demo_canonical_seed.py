from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.app.models import CanonicalPassage, CanonicalWork
from services.api.app.services.canonical_corpus import locator_sort_key, normalize_locator, source_authority_score


DEMO_WORKS: list[dict[str, Any]] = [
    {
        "work_key": "bhagavad_gita",
        "title_sa": "Bhagavad Gita",
        "title_hi": "Bhagavad Gita",
        "title_en": "Bhagavad Gita",
        "category": "gita",
        "tradition_scope": ["vaidika", "yoga", "vedanta"],
        "authority_level": "PRIMARY",
        "canonical_status": "VERIFIED",
        "metadata_json": {"seed": "demo", "rights_basis": "public_domain_review_required"},
    },
    {
        "work_key": "isha_upanishad",
        "title_sa": "Isha Upanishad",
        "title_hi": "Isha Upanishad",
        "title_en": "Isha Upanishad",
        "category": "upanishad",
        "tradition_scope": ["vaidika", "vedanta"],
        "authority_level": "PRIMARY",
        "canonical_status": "VERIFIED",
        "metadata_json": {"seed": "demo", "rights_basis": "public_domain_review_required"},
    },
]


DEMO_PASSAGES: list[dict[str, Any]] = [
    {
        "work_key": "bhagavad_gita",
        "locator": "2.47",
        "sanskrit_text": "karmany evadhikaras te ma phalesu kadacana",
        "normalized_text": "You have a claim over action, not over the fruits of action.",
        "translation_hi": "Karma par adhikar hai, phal par asakti nahi.",
        "translation_en": "Your responsibility is action, without attachment to its result.",
        "chapter": "2",
        "verse": "47",
        "confidence": 0.92,
        "review_status": "VERIFIED",
    },
    {
        "work_key": "bhagavad_gita",
        "locator": "4.7",
        "sanskrit_text": "yada yada hi dharmasya glanir bhavati bharata",
        "normalized_text": "Whenever dharma declines, restoration becomes necessary.",
        "translation_hi": "Jab jab dharma ki glani hoti hai, tab samyak sthapana ki avashyakta hoti hai.",
        "translation_en": "When dharma declines, restoration of order is required.",
        "chapter": "4",
        "verse": "7",
        "confidence": 0.88,
        "review_status": "VERIFIED",
    },
    {
        "work_key": "isha_upanishad",
        "locator": "1",
        "sanskrit_text": "isavasyam idam sarvam",
        "normalized_text": "All this is pervaded by the divine.",
        "translation_hi": "Yah sampurna jagat ishavasyam hai.",
        "translation_en": "All existence is pervaded by the divine reality.",
        "section": "mantra",
        "verse": "1",
        "confidence": 0.9,
        "review_status": "VERIFIED",
    },
]


async def seed_demo_canonical(session: AsyncSession) -> dict[str, Any]:
    work_key_to_id: dict[str, str] = {}
    inserted_works = 0
    inserted_passages = 0

    for payload in DEMO_WORKS:
        result = await session.execute(select(CanonicalWork).where(CanonicalWork.work_key == payload["work_key"]))
        row = result.scalars().first()
        if row is None:
            row = CanonicalWork(**payload)
            session.add(row)
            await session.flush()
            inserted_works += 1
        work_key_to_id[row.work_key] = row.id

    for payload in DEMO_PASSAGES:
        work_id = work_key_to_id[payload["work_key"]]
        locator = normalize_locator(payload["locator"])
        result = await session.execute(
            select(CanonicalPassage).where(
                CanonicalPassage.work_id == work_id,
                CanonicalPassage.locator == locator,
            )
        )
        if result.scalars().first() is not None:
            continue
        passage_payload = {key: value for key, value in payload.items() if key != "work_key"}
        work = await session.get(CanonicalWork, work_id)
        row = CanonicalPassage(
            **{key: value for key, value in passage_payload.items() if key != "locator"},
            work_id=work_id,
            locator=locator,
            locator_sort_key=locator_sort_key(locator),
            source_ids=[],
            authority_score=source_authority_score(
                work.authority_level if work else "PRIMARY",
                passage_payload.get("review_status", "VERIFIED"),
                passage_payload.get("confidence", 0.9),
            ),
            metadata_json={"seed": "demo"},
        )
        session.add(row)
        inserted_passages += 1

    await session.commit()
    return {
        "imported": {"works": inserted_works, "passages": inserted_passages},
        "totals": {"works": len(DEMO_WORKS), "passages": len(DEMO_PASSAGES)},
    }
