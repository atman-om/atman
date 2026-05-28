from services.api.app.services.corpus_review import can_promote_source, distribution


def test_z2_blocks_unknown_rights() -> None:
    check = can_promote_source(target_status="APPROVED_Z2", rights_status="UNKNOWN")
    assert not check.allowed
    assert "Z2" in (check.reason or "")


def test_z2_allows_public_domain() -> None:
    check = can_promote_source(target_status="APPROVED_Z2", rights_status="PUBLIC_DOMAIN_VERIFIED")
    assert check.allowed


def test_distribution_counts_unknown() -> None:
    assert distribution(["A", "A", None])["UNKNOWN"] == 1
