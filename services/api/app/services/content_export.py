from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Protocol, Any


class ExportableContentItem(Protocol):
    id: str
    batch_id: str | None
    title: str | None
    content_type: str
    topic: str
    language: str
    body: str
    source_chunk_ids: list[str]
    quality_report: dict[str, Any]
    review_status: str
    version: int
    provenance: dict[str, Any]


@dataclass(frozen=True)
class ExportPayload:
    path: Path
    item_count: int
    manifest: dict[str, Any]


def _item_dict(item: ExportableContentItem) -> dict[str, Any]:
    return {
        "id": item.id,
        "batch_id": item.batch_id,
        "title": item.title,
        "content_type": item.content_type,
        "topic": item.topic,
        "language": item.language,
        "body": item.body,
        "source_chunk_ids": item.source_chunk_ids,
        "quality_report": item.quality_report,
        "review_status": item.review_status,
        "version": item.version,
        "provenance": item.provenance,
    }


def export_items_to_file(
    items: Iterable[ExportableContentItem],
    *,
    export_format: str,
    export_dir: Path,
    stem: str,
) -> ExportPayload:
    rows = list(items)
    export_dir.mkdir(parents=True, exist_ok=True)
    safe_stem = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in stem)[:120] or "content_export"

    if export_format == "jsonl":
        path = export_dir / f"{safe_stem}.jsonl"
        with path.open("w", encoding="utf-8") as f:
            for item in rows:
                f.write(json.dumps(_item_dict(item), ensure_ascii=False) + "\n")
    elif export_format == "markdown":
        path = export_dir / f"{safe_stem}.md"
        with path.open("w", encoding="utf-8") as f:
            f.write(f"# Atman Content Export: {safe_stem}\n\n")
            for item in rows:
                f.write(f"## {item.title or item.topic}\n\n")
                f.write(f"- ID: `{item.id}`\n")
                f.write(f"- Type: `{item.content_type}`\n")
                f.write(f"- Review: `{item.review_status}`\n")
                f.write(f"- Source chunks: `{', '.join(item.source_chunk_ids or [])}`\n\n")
                f.write(item.body.strip() + "\n\n---\n\n")
    elif export_format == "csv":
        path = export_dir / f"{safe_stem}.csv"
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["id", "batch_id", "title", "content_type", "topic", "language", "review_status", "body"],
            )
            writer.writeheader()
            for item in rows:
                writer.writerow(
                    {
                        "id": item.id,
                        "batch_id": item.batch_id,
                        "title": item.title or "",
                        "content_type": item.content_type,
                        "topic": item.topic,
                        "language": item.language,
                        "review_status": item.review_status,
                        "body": item.body,
                    }
                )
    else:
        raise ValueError(f"unsupported export format: {export_format}")

    manifest = {
        "export_format": export_format,
        "item_count": len(rows),
        "file_name": path.name,
        "review_statuses": sorted({item.review_status for item in rows}),
    }
    return ExportPayload(path=path, item_count=len(rows), manifest=manifest)
