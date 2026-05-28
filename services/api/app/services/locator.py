from __future__ import annotations
import re
from dataclasses import dataclass

_LOCATOR_RE = re.compile(
    r"^(?P<work>[A-Z][A-Z0-9_]+)(?:\.(?P<section>[A-Z0-9_]+))*\.(?P<num1>\d+)(?:\.(?P<num2>\d+))?$"
)


@dataclass(frozen=True)
class LocatorValidation:
    locator: str
    valid: bool
    reason: str | None = None


def validate_locator(locator: str) -> LocatorValidation:
    value = locator.strip()
    if not value:
        return LocatorValidation(locator=locator, valid=False, reason="empty locator")
    if len(value) > 160:
        return LocatorValidation(locator=locator, valid=False, reason="locator too long")
    if not _LOCATOR_RE.match(value):
        return LocatorValidation(locator=locator, valid=False, reason="does not match Atman source locator grammar")
    return LocatorValidation(locator=value, valid=True)


def chunk_locator(base_locator: str | None, order: int) -> dict[str, object]:
    if base_locator:
        validation = validate_locator(base_locator)
        return {
            "locator": validation.locator if validation.valid else None,
            "valid": validation.valid,
            "reason": validation.reason,
            "chunk_order": order,
        }
    return {"locator": None, "valid": False, "reason": "missing source locator", "chunk_order": order}
