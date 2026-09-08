from evaluation.llm_response_scorers import score_contains_expected_fact
from evaluation.quality_gate import evaluate_quality_gate


def test_quality_gate_passes_for_valid_llm_response():
    result = score_contains_expected_fact(
        "The order service is unavailable.",
        "order service is unavailable",
    )

    result["required"] = True
    result["threshold"] = 1.0

    gate = evaluate_quality_gate([result])

    assert gate["status"] == "PASS"
    assert gate["failed_required_scorers"] == 0


def test_quality_gate_fails_for_invalid_llm_response():
    result = score_contains_expected_fact(
        "The order service is healthy.",
        "order service is unavailable",
    )

    result["required"] = True
    result["threshold"] = 1.0

    gate = evaluate_quality_gate([result])

    assert gate["status"] == "FAIL"
    assert gate["failed_required_scorers"] == 1