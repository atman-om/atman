from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import re


@dataclass(frozen=True)
class OCRAnalysis:
    filename: str
    status: str
    engine: str
    text: str | None
    text_hash: str | None
    confidence: float
    page_count: int
    warnings: list[str]
    report: dict[str, object]


def _decode_text(raw: bytes) -> str | None:
    for encoding in ("utf-8", "utf-16", "latin-1"):
        try:
            text = raw.decode(encoding)
        except UnicodeDecodeError:
            continue
        printable_ratio = sum(ch.isprintable() or ch.isspace() for ch in text) / max(len(text), 1)
        if printable_ratio > 0.88:
            return text
    return None


def normalize_ocr_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def analyze_document_for_ocr(filename: str, raw: bytes, *, engine: str = "deterministic") -> OCRAnalysis:
    suffix = Path(filename).suffix.lower().lstrip(".")
    warnings: list[str] = []
    text: str | None = None
    page_count = 1
    status = "TEXT_EXTRACTED"
    confidence = 0.0

    decoded = _decode_text(raw)
    if decoded and suffix in {"txt", "md", "html", "htm", "csv", "json"}:
        text = normalize_ocr_text(decoded)
        confidence = min(0.99, max(0.7, len(text) / 5000))
    elif suffix == "pdf":
        # Deterministic mode does not perform bitmap OCR. It identifies whether a PDF
        # likely needs a real OCR engine and records the correct status for review.
        decoded_pdf = decoded or ""
        page_count = max(1, decoded_pdf.count("/Page"))
        if len(decoded_pdf) > 0 and any(marker in decoded_pdf for marker in ("BT", "Tj", "TJ")):
            text = normalize_ocr_text(re.sub(r"[^\w\s\-.,:;!?()\[\]{}'\"/\\]+", " ", decoded_pdf))[:12000]
            confidence = 0.45
            warnings.append("PDF text-layer extraction is heuristic; route to review before Z2.")
        else:
            status = "OCR_REQUIRED"
            warnings.append("PDF appears image-based or encrypted; configure Tesseract/PaddleOCR/external OCR.")
    elif suffix in {"png", "jpg", "jpeg", "webp", "tiff", "tif"}:
        status = "OCR_REQUIRED"
        warnings.append("Image file requires real OCR engine; deterministic mode only records the job.")
    else:
        if decoded:
            text = normalize_ocr_text(decoded)
            confidence = 0.55
            warnings.append("Unknown extension decoded as text; manual review required.")
        else:
            status = "UNSUPPORTED_BINARY"
            warnings.append("Unsupported binary format for deterministic OCR analysis.")

    if text and len(text) < 20:
        warnings.append("Extracted text is very short; likely incomplete.")
    text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest() if text else None
    return OCRAnalysis(
        filename=filename,
        status=status,
        engine=engine,
        text=text,
        text_hash=text_hash,
        confidence=confidence,
        page_count=page_count,
        warnings=warnings,
        report={
            "suffix": suffix,
            "bytes": len(raw),
            "deterministic": engine == "deterministic",
            "needs_review": status != "TEXT_EXTRACTED" or confidence < 0.8,
        },
    )
