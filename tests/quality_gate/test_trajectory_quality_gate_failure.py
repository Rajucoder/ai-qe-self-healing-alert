from evaluation.quality_gate import evaluate_quality_gate
from evaluation.trajectory_scorers import (
    score_forbidden_tools,
    score_tool_trajectory,
)


def test_quality_gate_fails_for_wrong_agent_trajectory():
    actual_tools = [
        "check_database",
        "check_service",
        "check_logs",
        "restart_service",
        "validate_service",
    ]

    # Deliberately incorrect expectation.
    expected_tools = [
        "check_database",
        "check_service",
        "restart_service",
        "check_logs",
        "validate_service",
    ]

    forbidden_tools = [
        "create_incident",
    ]

    trajectory_result = score_tool_trajectory(
        actual_tools,
        expected_tools,
    )
    trajectory_result["required"] = True

    forbidden_result = score_forbidden_tools(
        actual_tools,
        forbidden_tools,
    )
    forbidden_result["required"] = True

    scorer_results = [
        trajectory_result,
        forbidden_result,
    ]

    quality_gate_result = evaluate_quality_gate(
        scorer_results
    )

    assert trajectory_result["score"] == 0.0
    assert trajectory_result["passed"] is False

    assert forbidden_result["score"] == 1.0
    assert forbidden_result["passed"] is True

    assert quality_gate_result["status"] == "FAIL"
    assert quality_gate_result["failed_required_scorers"] == 1