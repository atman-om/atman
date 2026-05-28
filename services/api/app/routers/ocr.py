from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.app.core.config import get_settings
from services.api.app.core.db import get_session
from services.api.app.models import OCRJob
from services.api.app.schemas import OCRAnalyzeResponse
from services.api.app.services.ocr import analyze_document_for_ocr

router = APIRouter(prefix="/ocr", tags=["ocr"])


@router.post("/analyze", response_model=OCRAnalyzeResponse)
async def analyze_upload_for_ocr(file: UploadFile = File(...), session: AsyncSession = Depends(get_session)) -> OCRAnalyzeResponse:
    settings = get_settings()
    raw = await file.read()
    result = analyze_document_for_ocr(file.filename or "upload.bin", raw, engine=settings.ocr_mode)
    output_uri = None
    if result.text:
        Path(settings.ocr_output_dir).mkdir(parents=True, exist_ok=True)
        safe = (file.filename or "upload").replace("/", "_").replace("\\", "_")
        out_path = Path(settings.ocr_output_dir) / f"{safe}.txt"
        out_path.write_text(result.text, encoding="utf-8")
        output_uri = str(out_path)
    job = OCRJob(
        filename=result.filename,
        status=result.status,
        engine=result.engine,
        page_count=result.page_count,
        confidence=result.confidence,
        text_hash=result.text_hash,
        output_uri=output_uri,
        report=result.report | {"warnings": result.warnings},
    )
    session.add(job)
    await session.commit()
    return OCRAnalyzeResponse(**result.__dict__)
