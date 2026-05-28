from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.app.core.config import get_settings
from services.api.app.core.db import get_session
from services.api.app.models import ClaimEvidenceReview
from services.api.app.schemas import ClaimCheckOut, ClaimCheckRequest
from services.api.app.services.source_correctness import grade_claim_against_evidence, public_claim_allowed

router = APIRouter(prefix="/correctness", tags=["source-correctness-v2.0"])


@router.post("/claims/check", response_model=ClaimCheckOut)
async def check_claim(payload: ClaimCheckRequest, session: AsyncSession = Depends(get_session)) -> ClaimCheckOut:
    settings = get_settings()
    report = grade_claim_against_evidence(payload.claim, payload.candidate_evidence, strictness=payload.strictness)
    min_grade = settings.correctness_min_public_grade if payload.public_answer else "C"
    if payload.public_answer and not public_claim_allowed(report["support_grade"], min_grade=min_grade):
        report["verdict"] = "BLOCK_OR_SHOW_UNCERTAINTY"
        report.setdefault("warnings", []).append("below_public_answer_grade_threshold")
    row = ClaimEvidenceReview(claim_text=payload.claim, support_grade=report["support_grade"], verdict=report["verdict"], evidence=report["evidence"], reviewer_notes="auto_check")
    session.add(row)
    await session.commit()
    return ClaimCheckOut(claim=payload.claim, **report)
