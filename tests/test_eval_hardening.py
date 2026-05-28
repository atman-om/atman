from services.api.app.services.eval_hardening import (
    check_citation_alignment,
    check_fake_shloka,
    compute_release_readiness,
    load_cases,
)


def test_hardened_cases_load() -> None:
    cases = load_cases("nyayabench_*_seed.jsonl", benchmark_name="nyayabench_hardened")
    assert cases
    assert any(case.category == "fake_shloka" for case in cases)


def test_citation_alignment_strict_passes_with_locator_hit() -> None:
    report = check_citation_alignment("स्रोत: BG.2.47", [{"locator": "BG.2.47", "source_id": "s1", "chunk_id": "c1"}], strict=True)
    assert report["passed"]
    assert report["alignment_score"] >= 0.95


def test_citation_alignment_blocks_fake_marker_without_citation() -> None:
    report = check_citation_alignment("स्रोत: BG.2.47", [], strict=True)
    assert not report["passed"]
    assert "BG." in report["unsupported_markers"]


def test_fake_shloka_blocks_uncited_devanagari_quote() -> None:
    report = check_fake_shloka("धर्मो रक्षति रक्षितः ॥", [], strict=True)
    assert not report["passed"]
    assert report["risk_score"] == 1.0


def test_release_readiness_blocks_hard_failure() -> None:
    readiness = compute_release_readiness(
        [{"passed": False, "severity": "hard_fail", "score": 0, "category": "fake_shloka"}],
        {"fake_shloka": {"hard_failures": 1, "pass_rate": 0.0}},
        [{"case_id": "x"}],
    )
    assert not readiness["allowed"]
