from pathlib import Path
from types import SimpleNamespace

from services.api.app.services.content_export import export_items_to_file


def fake_item(idx: int):
    return SimpleNamespace(
        id=f"item-{idx}", batch_id="batch-1", title=f"Title {idx}", content_type="notes",
        topic="कर्मयोग", language="hi", body="body", source_chunk_ids=["c1"],
        quality_report={"score": 1}, review_status="APPROVED", version=1, provenance={}
    )


def test_jsonl_export(tmp_path: Path) -> None:
    payload = export_items_to_file([fake_item(1), fake_item(2)], export_format="jsonl", export_dir=tmp_path, stem="test")
    assert payload.path.exists()
    assert payload.item_count == 2
    assert len(payload.path.read_text(encoding="utf-8").splitlines()) == 2


def test_markdown_export(tmp_path: Path) -> None:
    payload = export_items_to_file([fake_item(1)], export_format="markdown", export_dir=tmp_path, stem="test_md")
    assert payload.path.suffix == ".md"
    assert "Title 1" in payload.path.read_text(encoding="utf-8")
