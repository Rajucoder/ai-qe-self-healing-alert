def score_expected_evidence(
    answer: str,
    expected_evidence: list[str],
) -> dict:

    answer_lower = answer.lower()

    missing_evidence = [
        evidence
        for evidence in expected_evidence
        if evidence.lower() not in answer_lower
    ]

    passed = len(missing_evidence) == 0

    return {
        "passed": passed,
        "missing_evidence": missing_evidence,
        "score": 1.0 if passed else 0.0,
    }


def score_abstention(
    answer: str,
    expected_evidence: list[str],
) -> dict:

    if expected_evidence:
        return {
            "passed": True,
            "score": 1.0,
            "reason": "Abstention check not required.",
        }

    abstention_phrases = [
        "does not contain",
        "not available",
        "information is not available",
        "not enough information",
    ]

    answer_lower = answer.lower()

    matched = [
        phrase
        for phrase in abstention_phrases
        if phrase in answer_lower
    ]

    passed = len(matched) > 0

    return {
        "passed": passed,
        "score": 1.0 if passed else 0.0,
        "matched_phrases": matched,
    }