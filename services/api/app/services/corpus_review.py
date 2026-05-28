from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable

from services.api.app.domain.enums import RightsStatus


RIGHTS_ALLOWED_FOR_Z2 = {
    RightsStatus.PUBLIC_DOMAIN_VERIFIED.value,
    RightsStatus.LICENSED_VERIFIED.value,
    RightsStatus.OPEN_LICENSE_VERIFIED.value,
    RightsStatus.USER_OWNED.value,
    RightsStatus.NO_TRAINING_ALLOWED.value,
}


@dataclass(frozen=True)
class PromotionCheck:
    allowed: bool
    reason: str | None = None


def can_promote_source(*, target_status: str, rights_status: str, require_rights_for_z2: bool = True) -> PromotionCheck:
    if target_status == "APPROVED_Z1":
        if rights_status in {RightsStatus.REJECTED.value, RightsStatus.NO_STORAGE_ALLOWED.value}:
            return PromotionCheck(False, "rights status blocks sandbox approval")
        return PromotionCheck(True)
    if target_status == "APPROVED_Z2":
        if require_rights_for_z2 and rights_status not in RIGHTS_ALLOWED_FOR_Z2:
            return PromotionCheck(False, "Z2 requires verified storage/RAG-safe rights")
        return PromotionCheck(True)
    if target_status in {"BLOCKED", "DEPRECATED"}:
        return PromotionCheck(True)
    return PromotionCheck(False, f"unsupported target status: {target_status}")


def distribution(values: Iterable[str | None]) -> dict[str, int]:
    return dict(Counter(v or "UNKNOWN" for v in values))
