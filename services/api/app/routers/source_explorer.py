from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.app.core.db import get_session
from services.api.app.deps import require_admin
from services.api.app.schemas import SourceExplorerDetailOut, SourceExplorerSearchResponse
from services.api.app.services.source_explorer import get_source_detail, search_sources

router = APIRouter(tags=["source-explorer"])


@router.get("/public/source-explorer/search", response_model=SourceExplorerSearchResponse)
async def public_source_explorer_search(
    q: str | None = Query(default=None, max_length=512),
    language: str | None = Query(default=None, max_length=32),
    limit: int = Query(default=25, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> SourceExplorerSearchResponse:
    result = await search_sources(
        session,
        query=q,
        language=language,
        rights_status=[],
        ingestion_status=[],
        public_only=True,
        limit=limit,
    )
    return SourceExplorerSearchResponse(**result.__dict__)


@router.get("/public/source-explorer/sources/{source_id}", response_model=SourceExplorerDetailOut)
async def public_source_explorer_detail(source_id: str, session: AsyncSession = Depends(get_session)) -> SourceExplorerDetailOut:
    detail = await get_source_detail(session, source_id=source_id, public_only=True)
    if detail is None:
        raise HTTPException(status_code=404, detail="public source not found")
    return SourceExplorerDetailOut(**detail)


@router.get("/source-explorer/search", response_model=SourceExplorerSearchResponse)
async def admin_source_explorer_search(
    q: str | None = Query(default=None, max_length=512),
    language: str | None = Query(default=None, max_length=32),
    rights_status: list[str] = Query(default=[]),
    ingestion_status: list[str] = Query(default=[]),
    public_only: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=250),
    session: AsyncSession = Depends(get_session),
    _admin=Depends(require_admin),
) -> SourceExplorerSearchResponse:
    result = await search_sources(
        session,
        query=q,
        language=language,
        rights_status=rights_status,
        ingestion_status=ingestion_status,
        public_only=public_only,
        limit=limit,
    )
    return SourceExplorerSearchResponse(**result.__dict__)


@router.get("/source-explorer/sources/{source_id}", response_model=SourceExplorerDetailOut)
async def admin_source_explorer_detail(
    source_id: str,
    public_only: bool = Query(default=False),
    session: AsyncSession = Depends(get_session),
    _admin=Depends(require_admin),
) -> SourceExplorerDetailOut:
    detail = await get_source_detail(session, source_id=source_id, public_only=public_only)
    if detail is None:
        raise HTTPException(status_code=404, detail="source not found")
    return SourceExplorerDetailOut(**detail)
