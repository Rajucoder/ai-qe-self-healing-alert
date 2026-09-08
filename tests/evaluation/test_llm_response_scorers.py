from evaluation.llm_response_scorers import score_contains_expected_fact, score_forbidden_claim


def test_expected_fact_found():
    result = score_contains_expected_fact(
        "The order service is unavailable.",
        "order service is unavailable",
    )

    assert result["score"] == 1.0
    assert result["passed"] is True


def test_expected_fact_missing():
    result = score_contains_expected_fact(
        "The order service is healthy.",
        "order service is unavailable",
    )

    assert result["score"] == 0.0
    assert result["passed"] is False

def test_forbidden_claim_fails_when_claim_is_present():
    result = score_forbidden_claim(
        "No investigation could be performed due to lack of access to diagnostic tools.",
        "lack of access to diagnostic tools",
    )

    assert result["score"] == 0.0
    assert result["passed"] is False


def test_forbidden_claim_passes_when_claim_is_absent():
    result = score_forbidden_claim(
        "The service was investigated using the available diagnostic tools.",
        "lack of access to diagnostic tools",
    )

    assert result["score"] == 1.0
    assert result["passed"] is True