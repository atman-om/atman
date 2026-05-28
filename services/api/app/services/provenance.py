from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
import hashlib
import json


@dataclass(frozen=True)
class ProvenanceRecord:
    object_type: str
    object_id: str
    event_type: str
    evidence: dict[str, Any]
    evidence_hash: str
    created_at: str


def build_provenance_record(object_type: str, object_id: str, event_type: str, evidence: dict[str, Any]) -> ProvenanceRecord:
    canonical = json.dumps(evidence, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return ProvenanceRecord(
        object_type=object_type,
        object_id=object_id,
        event_type=event_type,
        evidence=evidence,
        evidence_hash=hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        created_at=datetime.now(timezone.utc).isoformat(),
    )
