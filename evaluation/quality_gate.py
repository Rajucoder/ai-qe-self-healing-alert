def evaluate_quality_gate(results):
    """
    Determine whether the overall quality gate passes.

    A required scorer fails the gate when its score is below
    its configured threshold.

    Non-required scorer failures do not block the gate.
    """

    evaluated_results = []

    for result in results:
        threshold = result.get("threshold", 1.0)
        passed = result["score"] >= threshold

        evaluated_result = {
            **result,
            "threshold": threshold,
            "passed": passed,
        }

        evaluated_results.append(evaluated_result)

    failed_required = [
        result
        for result in evaluated_results
        if result["required"] and not result["passed"]
    ]

    return {
        "status": "PASS" if not failed_required else "FAIL",
        "failed_required_scorers": len(failed_required),
        "failed_results": failed_required,
        "results": evaluated_results,
    }