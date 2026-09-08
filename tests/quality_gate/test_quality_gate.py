from evaluation.quality_gate import evaluate_quality_gate


def test_quality_gate_passes_when_required_scorers_meet_threshold():
    results = [
        {
            "name": "tool_trajectory",
            "score": 1.0,
            "threshold": 1.0,
            "required": True,
            "reason": "Trajectory matched.",
        },
        {
            "name": "forbidden_tools",
            "score": 1.0,
            "threshold": 1.0,
            "required": True,
            "reason": "No forbidden tools.",
        },
    ]

    result = evaluate_quality_gate(results)

    assert result["status"] == "PASS"
    assert result["failed_required_scorers"] == 0


def test_quality_gate_fails_when_required_score_is_below_threshold():
    results = [
        {
            "name": "tool_trajectory",
            "score": 0.72,
            "threshold": 0.85,
            "required": True,
            "reason": "Trajectory did not meet threshold.",
        }
    ]

    result = evaluate_quality_gate(results)

    assert result["status"] == "FAIL"
    assert result["failed_required_scorers"] == 1
    assert result["failed_results"][0]["name"] == "tool_trajectory"


def test_quality_gate_ignores_non_required_failure():
    results = [
        {
            "name": "tool_trajectory",
            "score": 1.0,
            "threshold": 1.0,
            "required": True,
            "reason": "Trajectory matched.",
        },
        {
            "name": "optional_style",
            "score": 0.50,
            "threshold": 0.80,
            "required": False,
            "reason": "Style score below target.",
        },
    ]

    result = evaluate_quality_gate(results)

    assert result["status"] == "PASS"
    assert result["failed_required_scorers"] == 0