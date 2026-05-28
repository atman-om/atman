from __future__ import annotations

import hashlib
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.app.core.config import get_settings
from services.api.app.core.db import get_session
from services.api.app.models import ModelCheckpoint, ModelRelease, TrainingDataset, TrainingRun
from services.api.app.schemas import (
    ModelCheckpointOut,
    ModelReleaseOut,
    ModelReleaseRequest,
    TrainingDatasetBuildRequest,
    TrainingDatasetOut,
    TrainingRunOut,
    TrainingRunStartRequest,
)
from services.api.app.services.modelops import evaluate_model_release_gate
from services.api.app.services.training import build_training_dataset, qlora_config, simulate_training_metrics, write_dataset_artifact

router = APIRouter(prefix="/training", tags=["training-modelops"])


@router.post("/datasets/build", response_model=TrainingDatasetOut)
async def build_dataset(payload: TrainingDatasetBuildRequest, session: AsyncSession = Depends(get_session)) -> TrainingDatasetOut:
    settings = get_settings()
    samples = [sample.model_dump() for sample in payload.samples]
    report = build_training_dataset(samples, name=payload.name, base_model=payload.base_model)
    artifact_uri = write_dataset_artifact(settings.training_artifact_dir, payload.name, report)
    row = TrainingDataset(
        name=payload.name,
        base_model=payload.base_model,
        sample_count=report.sample_count,
        artifact_uri=artifact_uri,
        manifest=report.manifest,
        status="BUILT" if report.sample_count else "EMPTY",
    )
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return TrainingDatasetOut.model_validate(row)


@router.post("/runs/start", response_model=TrainingRunOut)
async def start_training_run(payload: TrainingRunStartRequest, session: AsyncSession = Depends(get_session)) -> TrainingRunOut:
    settings = get_settings()
    dataset = await session.get(TrainingDataset, payload.dataset_id) if payload.dataset_id else None
    if payload.dataset_id and dataset is None:
        raise HTTPException(status_code=404, detail="dataset not found")
    if not payload.simulate and not settings.training_allow_real_jobs:
        raise HTTPException(status_code=409, detail="real training jobs are disabled; set ATMAN_TRAINING_ALLOW_REAL_JOBS=true")
    sample_count = dataset.sample_count if dataset else 0
    config = qlora_config(
        base_model=payload.base_model,
        rank=settings.training_lora_rank,
        alpha=settings.training_lora_alpha,
        learning_rate=settings.training_learning_rate,
        epochs=settings.training_epochs,
    ) | payload.config
    metrics = simulate_training_metrics(sample_count)
    run = TrainingRun(
        dataset_id=payload.dataset_id,
        base_model=payload.base_model,
        adapter_method=payload.adapter_method,
        status="SIMULATED_COMPLETED" if payload.simulate else "QUEUED",
        config=config,
        metrics=metrics,
    )
    session.add(run)
    await session.flush()
    if payload.simulate:
        checkpoint = ModelCheckpoint(
            run_id=run.id,
            model_name=f"Atman-Lab-Qwen-14B-v1.0-{str(uuid4())[:8]}",
            base_model=payload.base_model,
            adapter_uri=str(Path(settings.training_artifact_dir) / "adapters" / f"{run.id}.safetensors"),
            checksum_sha256=hashlib.sha256(run.id.encode("utf-8")).hexdigest(),
            eval_summary={"score": metrics["citation_obedience_probe"], "hard_failures": []},
            release_status="UNRELEASED",
        )
        session.add(checkpoint)
        await session.flush()
        run.checkpoint_id = checkpoint.id
    await session.commit()
    await session.refresh(run)
    return TrainingRunOut.model_validate(run)


@router.get("/runs/{run_id}", response_model=TrainingRunOut)
async def get_training_run(run_id: str, session: AsyncSession = Depends(get_session)) -> TrainingRunOut:
    row = await session.get(TrainingRun, run_id)
    if row is None:
        raise HTTPException(status_code=404, detail="training run not found")
    return TrainingRunOut.model_validate(row)


@router.get("/checkpoints", response_model=list[ModelCheckpointOut])
async def list_checkpoints(limit: int = Query(default=50, ge=1, le=250), session: AsyncSession = Depends(get_session)) -> list[ModelCheckpointOut]:
    result = await session.execute(select(ModelCheckpoint).order_by(ModelCheckpoint.created_at.desc()).limit(limit))
    return [ModelCheckpointOut.model_validate(row) for row in result.scalars().all()]


@router.post("/checkpoints/{checkpoint_id}/release", response_model=ModelReleaseOut)
async def release_checkpoint(checkpoint_id: str, payload: ModelReleaseRequest, session: AsyncSession = Depends(get_session)) -> ModelReleaseOut:
    settings = get_settings()
    checkpoint = await session.get(ModelCheckpoint, checkpoint_id)
    if checkpoint is None:
        raise HTTPException(status_code=404, detail="checkpoint not found")
    eval_summary = payload.eval_summary or checkpoint.eval_summary or {}
    gate = evaluate_model_release_gate(
        eval_summary,
        min_score=settings.model_release_min_eval_score,
        require_no_hard_failures=settings.model_release_require_no_hard_failures,
        required_approvals=payload.required_approvals,
    )
    checkpoint.release_status = "RELEASED" if gate.allowed else "BLOCKED"
    row = ModelRelease(
        checkpoint_id=checkpoint.id,
        release_name=payload.release_name,
        environment=payload.environment,
        allowed=gate.allowed,
        gate_report=gate.gate_report,
    )
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return ModelReleaseOut.model_validate(row)
