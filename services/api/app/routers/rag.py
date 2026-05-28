from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.app.core.config import get_settings
from services.api.app.core.db import get_session
from services.api.app.deps import get_vector_store
from services.api.app.schemas import RagQueryRequest, RagQueryResponse
from services.api.app.services.rag import answer_question

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/query", response_model=RagQueryResponse)
async def rag_query(payload: RagQueryRequest, session: AsyncSession = Depends(get_session)) -> RagQueryResponse:
    return await answer_question(
        session,
        question=payload.question,
        top_k=payload.top_k,
        settings=get_settings(),
        vector_store=get_vector_store(),
    )
