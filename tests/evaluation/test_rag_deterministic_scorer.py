from evaluation.rag_deterministic_scorer import (
    score_abstention,
    score_expected_evidence,
)


def test_expected_evidence_present():

    answer = (
        "Before restarting the payment service, "
        "verify database connectivity."
    )

    result = score_expected_evidence(
        answer,
        ["database connectivity"],
    )

    assert result["passed"] is True
    assert result["score"] == 1.0


def test_expected_evidence_missing():

    answer = (
        "Restart the payment service and validate its health."
    )

    result = score_expected_evidence(
        answer,
        ["database connectivity"],
    )

    assert result["passed"] is False
    assert result["score"] == 0.0
    assert "database connectivity" in result["missing_evidence"]


def test_abstention_passes():

    answer = (
        "The retrieved context does not contain "
        "information about the maximum number of retries."
    )

    result = score_abstention(
        answer,
        [],
    )

    assert result["passed"] is True
    assert result["score"] == 1.0


def test_abstention_fails_when_model_invents_answer():

    answer = (
        "The maximum number of retries is three."
    )

    result = score_abstention(
        answer,
        [],
    )

    assert result["passed"] is False
    assert result["score"] == 0.0