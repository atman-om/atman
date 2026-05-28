from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.app.core.config import get_settings
from services.api.app.core.db import get_session
from services.api.app.models import CanonicalPassage, ChatFeedback, ContentItem, FailureCase, ModelCheckpoint, ModelLabExperiment, TrainingDataset
from services.api.app.schemas import ModelComparisonOut, ModelLabDatasetPlanOut, ModelLabDatasetPlanRequest, ModelLabExperimentCreate, ModelLabExperimentOut, ModelLabReadinessOut
from services.api.app.services.model_lab import compare_candidates, dataset_plan, default_training_config, readiness

router = APIRouter(prefix="/model-lab", tags=["model-lab-v2.0"])


async def count(session: AsyncSession, model) -> int:  # type: ignore[no-untyped-def]
    result = await session.execute(select(func.count(model.id)))
    return int(result.scalar() or 0)


@router.get("/readiness", response_model=ModelLabReadinessOut)
async def model_lab_readiness(session: AsyncSession = Depends(get_session)) -> ModelLabReadinessOut:
    counts = {
        "canonical_passages": await count(session, CanonicalPassage),
        "content_items": await count(session, ContentItem),
        "chat_feedback": await count(session, ChatFeedback),
        "training_datasets": await count(session, TrainingDataset),
        "failure_cases": await count(session, FailureCase),
    }
    return ModelLabReadinessOut(**readiness(counts, get_settings()))


@router.post("/dataset-plan", response_model=ModelLabDatasetPlanOut)
async def create_dataset_plan(payload: ModelLabDatasetPlanRequest) -> ModelLabDatasetPlanOut:
    observed = {"verified_qa": payload.verified_qa, "reviewed_content": payload.reviewed_content, "failure_corrections": payload.failure_corrections, "adversarial": payload.adversarial}
    report = dataset_plan(name=payload.name, base_model=payload.base_model, target_sample_count=payload.target_sample_count, observed=observed, include_raw_scraped=payload.include_raw_scraped, settings=get_settings())
    return ModelLabDatasetPlanOut(**report)


@router.post("/experiments", response_model=ModelLabExperimentOut)
async def create_experiment(payload: ModelLabExperimentCreate, session: AsyncSession = Depends(get_session)) -> ModelLabExperimentOut:
    settings = get_settings()
    training_config = default_training_config(settings) | payload.training_config
    eval_plan = {"benchmarks": ["nyayabench_hardened", "citation_alignment", "fake_shloka_traps"], "release_gate_score": settings.model_lab_release_gate_score} | payload.eval_plan
    row = ModelLabExperiment(**payload.model_dump(exclude={"training_config", "eval_plan"}), training_config=training_config, eval_plan=eval_plan, gate_report={"production_replacement_allowed": False})
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return ModelLabExperimentOut.model_validate(row)


@router.get("/experiments", response_model=list[ModelLabExperimentOut])
async def list_experiments(limit: int = Query(default=50, ge=1, le=250), session: AsyncSession = Depends(get_session)) -> list[ModelLabExperimentOut]:
    result = await session.execute(select(ModelLabExperiment).order_by(ModelLabExperiment.created_at.desc()).limit(limit))
    return [ModelLabExperimentOut.model_validate(row) for row in result.scalars().all()]


@router.get("/comparison", response_model=ModelComparisonOut)
async def comparison(limit: int = Query(default=20, ge=1, le=100), session: AsyncSession = Depends(get_session)) -> ModelComparisonOut:
    result = await session.execute(select(ModelCheckpoint).order_by(ModelCheckpoint.created_at.desc()).limit(limit))
    checkpoints = []
    for row in result.scalars().all():
        checkpoints.append({"id": row.id, "model_name": row.model_name, "eval_summary": row.eval_summary})
    return ModelComparisonOut(**compare_candidates(checkpoints, get_settings()))
