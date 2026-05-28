from __future__ import annotations

import re
from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

from services.api.app.services.hashutil import sha256_text


SUPPORTED_TEXT_SUFFIXES = {".txt", ".md", ".markdown", ".csv", ".json", ".jsonl", ".xml"}
SUPPORTED_HTML_SUFFIXES = {".html", ".htm"}
SUPPORTED_PDF_SUFFIXES = {".pdf"}


@dataclass(frozen=True)
class ExtractionResult:
    text: str
    source_type: str
    checksum_sha256: str
    page_count: int = 0
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def report(self) -> dict[str, Any]:
        return {
            "source_type": self.source_type,
            "checksum_sha256": self.checksum_sha256,
            "page_count": self.page_count,
            "text_chars": len(self.text),
            "warnings": self.warnings,
            "metadata": self.metadata,
        }


def extract_text_from_bytes(filename: str, payload: bytes, *, enable_pdf: bool = True) -> ExtractionResult:
    suffix = Path(filename).suffix.lower()
    if suffix in SUPPORTED_TEXT_SUFFIXES:
        text = _decode_text(payload)
        normalized = normalize_extracted_text(text)
        return ExtractionResult(
            text=normalized,
            source_type=_source_type_for_suffix(suffix),
            checksum_sha256=sha256_text(normalized),
            metadata={"parser": "plain_text"},
        )
    if suffix in SUPPORTED_HTML_SUFFIXES:
        text = _extract_html(payload)
        normalized = normalize_extracted_text(text)
        return ExtractionResult(
            text=normalized,
            source_type="html",
            checksum_sha256=sha256_text(normalized),
            metadata={"parser": "beautifulsoup"},
        )
    if suffix in SUPPORTED_PDF_SUFFIXES:
        if not enable_pdf:
            raise ValueError("PDF extraction is disabled by configuration")
        return _extract_pdf(payload)
    raise ValueError(f"Unsupported corpus file type: {suffix or '<none>'}")


def normalize_extracted_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _decode_text(payload: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            return payload.decode(encoding)
        except UnicodeDecodeError:
            continue
    return payload.decode("utf-8", errors="replace")


def _extract_html(payload: bytes) -> str:
    soup = BeautifulSoup(_decode_text(payload), "html.parser")
    for node in soup(["script", "style", "noscript"]):
        node.extract()
    return soup.get_text("\n")


def _extract_pdf(payload: bytes) -> ExtractionResult:
    try:
        from pypdf import PdfReader
    except Exception as exc:  # pragma: no cover - dependency is declared, guard retained for deployments
        raise RuntimeError("pypdf is required for PDF extraction") from exc
    reader = PdfReader(BytesIO(payload))
    pages: list[str] = []
    warnings: list[str] = []
    for index, page in enumerate(reader.pages):
        try:
            pages.append(page.extract_text() or "")
        except Exception as exc:  # defensive: one bad page should not kill the ledger
            warnings.append(f"page_{index + 1}_extract_failed:{exc.__class__.__name__}")
            pages.append("")
    normalized = normalize_extracted_text("\n\n".join(pages))
    if not normalized:
        warnings.append("OCR_REQUIRED_TEXT_LAYER_EMPTY")
    return ExtractionResult(
        text=normalized,
        source_type="pdf",
        checksum_sha256=sha256_text(normalized or "<empty-pdf-text-layer>"),
        page_count=len(reader.pages),
        warnings=warnings,
        metadata={"parser": "pypdf", "encrypted": bool(getattr(reader, "is_encrypted", False))},
    )


def _source_type_for_suffix(suffix: str) -> str:
    return {
        ".txt": "text",
        ".md": "markdown",
        ".markdown": "markdown",
        ".csv": "csv",
        ".json": "json",
        ".jsonl": "jsonl",
        ".xml": "xml",
    }.get(suffix, "text")
