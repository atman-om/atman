from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.app.core.db import get_session
from services.api.app.models import EvalCaseResult
from services.api.app.schemas import (
    CitationCheckRequest,
    CitationCheckResponse,
    EvalCaseResultOut,
    EvalHardeningRunOut,
    EvalHardeningRunRequest,
    EvalRunOut,
    EvalRunRequest,
    FakeShlokaCheckRequest,
    FakeShlokaCheckResponse,
)
from services.api.app.services.eval_hardening import (
    check_fake_shloka,
    persist_citation_check,
    run_hardened_eval,
)
from services.api.app.services.eval_runner import run_seed_eval

router = APIRouter(prefix="/eval", tags=["eval"])


@router.post("/run", response_model=EvalRunOut)
async def run_eval(payload: EvalRunRequest, session: AsyncSession = Depends(get_session)) -> EvalRunOut:
    run = await run_seed_eval(
        session,
        model_version=payload.model_version,
        benchmark_name=payload.benchmark_name,
    )
    return EvalRunOut.model_validate(run)


@router.post("/run/hardened", response_model=EvalHardeningRunOut)
async def run_hardened(payload: EvalHardeningRunRequest, session: AsyncSession = Depends(get_session)) -> EvalHardeningRunOut:
    run, results, category_scores, release_readiness = await run_hardened_eval(
        session,
        model_version=payload.model_version,
        benchmark_name=payload.benchmark_name,
        dataset_glob=payload.dataset_glob,
        persist_cases=payload.persist_cases,
    )
    return EvalHardeningRunOut(
        run=EvalRunOut.model_validate(run),
        results=[EvalCaseResultOut.model_validate(row) for row in results],
        category_scores=category_scores,
        release_readiness=release_readiness,
    )


@router.get("/runs/{run_id}/results", response_model=list[EvalCaseResultOut])
async def get_run_results(run_id: str, session: AsyncSession = Depends(get_session)) -> list[EvalCaseResultOut]:
    result = await session.execute(select(EvalCaseResult).where(EvalCaseResult.eval_run_id == run_id).order_by(EvalCaseResult.created_at))
    rows = list(result.scalars().all())
    if not rows:
        raise HTTPException(status_code=404, detail="eval run results not found")
    return [EvalCaseResultOut.model_validate(row) for row in rows]


@router.post("/citation/check", response_model=CitationCheckResponse)
async def citation_check(payload: CitationCheckRequest, session: AsyncSession = Depends(get_session)) -> CitationCheckResponse:
    row = await persist_citation_check(session, payload.answer_text, payload.citations, payload.strict)
    return CitationCheckResponse(
        alignment_score=row.alignment_score,
        passed=row.passed,
        findings=row.findings,
        run_id=row.id,
    )


@router.post("/fake-shloka/check", response_model=FakeShlokaCheckResponse)
async def fake_shloka_check(payload: FakeShlokaCheckRequest) -> FakeShlokaCheckResponse:
    report = check_fake_shloka(payload.text, payload.citations, strict=payload.strict)
    return FakeShlokaCheckResponse(passed=report["passed"], risk_score=report["risk_score"], findings=report)
