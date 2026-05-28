from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.app.core.config import get_settings
from services.api.app.core.db import get_session
from services.api.app.models import BackupRun, ProductionIncident
from services.api.app.schemas import BackupRunOut, IncidentCreateRequest, IncidentOut, ProductionReadinessOut
from services.api.app.services.production import production_readiness, simulate_backup_manifest

router = APIRouter(prefix="/ops", tags=["production-ops"])


@router.get("/readiness", response_model=ProductionReadinessOut)
async def readiness() -> ProductionReadinessOut:
    return ProductionReadinessOut(**production_readiness(get_settings()))


@router.post("/backups/simulate", response_model=BackupRunOut)
async def simulate_backup(backup_type: str = "metadata", session: AsyncSession = Depends(get_session)) -> BackupRunOut:
    settings = get_settings()
    manifest = simulate_backup_manifest(settings, backup_type=backup_type)
    row = BackupRun(status="SIMULATED", backup_type=backup_type, artifact_uri=manifest["artifact_uri"], manifest=manifest)
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return BackupRunOut.model_validate(row)


@router.post("/incidents", response_model=IncidentOut)
async def create_incident(payload: IncidentCreateRequest, session: AsyncSession = Depends(get_session)) -> IncidentOut:
    row = ProductionIncident(severity=payload.severity, title=payload.title, description=payload.description, evidence=payload.evidence)
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return IncidentOut.model_validate(row)
