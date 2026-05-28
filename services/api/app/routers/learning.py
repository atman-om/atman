from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.app.core.db import get_session
from services.api.app.models import LearningPath, LessonProgress, ProductEvent, SavedAnswer
from services.api.app.schemas import LearningPathCreate, LearningPathOut, LessonProgressOut, LessonProgressUpdate, SavedAnswerCreate, SavedAnswerOut

router = APIRouter(prefix="/learning", tags=["learning-v2.0"])

DEFAULT_PATHS = [
    {"slug": "gita-foundations", "title": "गीता आधार पथ", "language": "hi", "difficulty": "beginner", "description": "कर्म, ज्ञान, भक्ति और अध्याय-दर-अध्याय गीता परिचय.", "canonical_work_keys": ["GITA"], "modules": [{"key": "gita-2", "title": "अध्याय 2: आत्मा, कर्म और स्थिरबुद्धि"}, {"key": "gita-3", "title": "अध्याय 3: कर्म योग"}], "status": "PUBLISHED"},
    {"slug": "upanishad-pravesh", "title": "उपनिषद प्रवेश", "language": "hi", "difficulty": "intermediate", "description": "ईश, कठ, केन और मुण्डक उपनिषद के मूल विचार.", "canonical_work_keys": ["ISHA_UP", "KATHA_UP"], "modules": [{"key": "isha-1", "title": "ईशावास्य का आरंभ"}], "status": "PUBLISHED"},
]


@router.get("/default-paths")
async def default_paths() -> list[dict[str, object]]:
    return DEFAULT_PATHS


@router.post("/paths", response_model=LearningPathOut)
async def create_path(payload: LearningPathCreate, session: AsyncSession = Depends(get_session)) -> LearningPathOut:
    row = LearningPath(**payload.model_dump())
    session.add(row)
    session.add(ProductEvent(event_type="learning_path_created", object_type="learning_path", object_id=row.id, event_metadata={"slug": row.slug}))
    await session.commit()
    await session.refresh(row)
    return LearningPathOut.model_validate(row)


@router.get("/paths", response_model=list[LearningPathOut])
async def list_paths(limit: int = Query(default=50, ge=1, le=250), session: AsyncSession = Depends(get_session)) -> list[LearningPathOut]:
    result = await session.execute(select(LearningPath).order_by(LearningPath.created_at.desc()).limit(limit))
    rows = result.scalars().all()
    if rows:
        return [LearningPathOut.model_validate(row) for row in rows]
    return [LearningPathOut(id=f"default-{i}", **path) for i, path in enumerate(DEFAULT_PATHS, start=1)]


@router.post("/progress", response_model=LessonProgressOut)
async def update_progress(payload: LessonProgressUpdate, session: AsyncSession = Depends(get_session)) -> LessonProgressOut:
    row = LessonProgress(**payload.model_dump())
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return LessonProgressOut.model_validate(row)


@router.post("/saved-answers", response_model=SavedAnswerOut)
async def save_answer(payload: SavedAnswerCreate, session: AsyncSession = Depends(get_session)) -> SavedAnswerOut:
    row = SavedAnswer(**payload.model_dump())
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return SavedAnswerOut.model_validate(row)


@router.get("/saved-answers", response_model=list[SavedAnswerOut])
async def list_saved_answers(user_id: str | None = None, limit: int = Query(default=50, ge=1, le=250), session: AsyncSession = Depends(get_session)) -> list[SavedAnswerOut]:
    stmt = select(SavedAnswer).order_by(SavedAnswer.created_at.desc()).limit(limit)
    if user_id:
        stmt = select(SavedAnswer).where(SavedAnswer.user_id == user_id).order_by(SavedAnswer.created_at.desc()).limit(limit)
    result = await session.execute(stmt)
    return [SavedAnswerOut.model_validate(row) for row in result.scalars().all()]
