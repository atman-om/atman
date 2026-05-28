from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.app.core.db import get_session
from services.api.app.models import AppUser, ProductEvent
from services.api.app.schemas import UserCreateRequest, UserOut

router = APIRouter(prefix="/accounts", tags=["accounts-v1.0.5"])


@router.post("/users", response_model=UserOut)
async def create_user(payload: UserCreateRequest, session: AsyncSession = Depends(get_session)) -> UserOut:
    row = AppUser(**payload.model_dump())
    session.add(row)
    try:
        await session.flush()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=409, detail="user email already exists") from exc
    session.add(ProductEvent(event_type="user_created", actor_id=row.id, object_type="app_user", object_id=row.id, event_metadata={"role": row.role}))
    await session.commit()
    await session.refresh(row)
    return UserOut.model_validate(row)


@router.get("/users", response_model=list[UserOut])
async def list_users(
    role: str | None = None,
    limit: int = Query(default=50, ge=1, le=250),
    session: AsyncSession = Depends(get_session),
) -> list[UserOut]:
    stmt = select(AppUser).order_by(AppUser.created_at.desc()).limit(limit)
    if role:
        stmt = select(AppUser).where(AppUser.role == role).order_by(AppUser.created_at.desc()).limit(limit)
    result = await session.execute(stmt)
    return [UserOut.model_validate(row) for row in result.scalars().all()]


@router.get("/me", response_model=UserOut)
async def demo_me(session: AsyncSession = Depends(get_session)) -> UserOut:
    result = await session.execute(select(AppUser).order_by(AppUser.created_at.asc()).limit(1))
    row = result.scalars().first()
    if row is None:
        row = AppUser(email="demo@atman.local", display_name="Atman Demo User", role="owner", preferences={"language": "hi", "citation_mode": "hidden"})
        session.add(row)
        await session.commit()
        await session.refresh(row)
    return UserOut.model_validate(row)
