from services.api.app.services.safety import evaluate_query_and_answer


def test_no_citation_flag() -> None:
    result = evaluate_query_and_answer("गीता क्या है?", "उत्तर", citations_count=0)
    assert "NO_CITATION" in result.flags


def test_unverified_sanskrit_blocks() -> None:
    result = evaluate_query_and_answer("श्लोक", "धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः ॥", citations_count=0)
    assert not result.allowed
