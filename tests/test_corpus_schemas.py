from services.api.app.schemas import ChunkReviewDecision, RightsDecisionRequest, SourcePromotionRequest


def test_rights_decision_schema() -> None:
    req = RightsDecisionRequest(rights_status="PUBLIC_DOMAIN_VERIFIED", evidence={"basis": "manual"})
    assert req.rights_status == "PUBLIC_DOMAIN_VERIFIED"


def test_source_promotion_schema() -> None:
    req = SourcePromotionRequest(target_status="APPROVED_Z2")
    assert req.target_status == "APPROVED_Z2"


def test_chunk_review_schema() -> None:
    req = ChunkReviewDecision(decision="approve", quality_score=0.9)
    assert req.quality_score == 0.9
