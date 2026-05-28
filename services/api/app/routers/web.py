from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.app.core.config import get_settings
from services.api.app.core.db import get_session
from services.api.app.schemas import WebSourceRequest, WebSourceOut
from services.api.app.services.web_corpus import register_web_source

router = APIRouter(prefix="/web-sources", tags=["web-corpus"])


@router.post("", response_model=WebSourceOut)
async def create_web_source(payload: WebSourceRequest, session: AsyncSession = Depends(get_session)) -> WebSourceOut:
    try:
        row = await register_web_source(
            session,
            url=str(payload.url),
            rights_status=payload.rights_status,
            fetch_now=payload.fetch_now,
            settings=get_settings(),
        )
    except PermissionError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return WebSourceOut.model_validate(row)
