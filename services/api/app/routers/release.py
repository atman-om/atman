from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.app.core.db import get_session
from services.api.app.models import ReleaseGate
from services.api.app.schemas import ReleaseGateRequest, ReleaseGateOut

router = APIRouter(prefix="/release-gates", tags=["release"])


@router.post("", response_model=ReleaseGateOut)
async def create_release_gate(payload: ReleaseGateRequest, session: AsyncSession = Depends(get_session)) -> ReleaseGateOut:
    allowed = not payload.hard_failures and payload.metrics.get("citation_validity", 0) >= 0.95
    gate = ReleaseGate(
        artifact_type=payload.artifact_type.value,
        artifact_version=payload.artifact_version,
        allowed=allowed,
        metrics=payload.metrics,
        hard_failures=payload.hard_failures,
        required_approvals=payload.required_approvals,
    )
    session.add(gate)
    await session.commit()
    await session.refresh(gate)
    return ReleaseGateOut.model_validate(gate)
