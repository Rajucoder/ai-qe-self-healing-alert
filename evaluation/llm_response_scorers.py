from __future__ import annotations


def score_contains_expected_fact(
    response: str,
    expected_fact: str,
) -> dict[str, object]:
    fact_found = expected_fact.lower() in response.lower()

    return {
        "name": "contains_expected_fact",
        "score": 1.0 if fact_found else 0.0,
        "passed": fact_found,
        "reason": (
            "Expected fact was found in the LLM response."
            if fact_found
            else "Expected fact was not found in the LLM response."
        ),
    }

def score_forbidden_claim(
    response: str,
    forbidden_claim: str,
) -> dict[str, object]:
    claim_found = forbidden_claim.lower() in response.lower()

    return {
        "name": "forbidden_claim",
        "score": 0.0 if claim_found else 1.0,
        "passed": not claim_found,
        "reason": (
            "Forbidden claim was not found in the LLM response."
            if not claim_found
            else f"Forbidden claim was found: {forbidden_claim}"
        ),
    }