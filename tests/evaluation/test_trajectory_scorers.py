from evaluation.trajectory_scorers import (
    score_forbidden_tools,
    score_tool_trajectory,
)


def test_tool_trajectory_passes():
    actual = [
        "check_database",
        "check_service",
        "check_logs",
    ]

    expected = [
        "check_database",
        "check_service",
        "check_logs",
    ]

    result = score_tool_trajectory(actual, expected)

    assert result["score"] == 1.0
    assert result["passed"] is True


def test_tool_trajectory_fails_when_order_is_wrong():
    actual = [
        "check_database",
        "check_logs",
        "check_service",
    ]

    expected = [
        "check_database",
        "check_service",
        "check_logs",
    ]

    result = score_tool_trajectory(actual, expected)

    assert result["score"] == 0.0
    assert result["passed"] is False


def test_forbidden_tools_pass():
    actual = [
        "check_database",
        "check_service",
        "check_logs",
    ]

    forbidden = [
        "restart_service",
        "create_incident",
    ]

    result = score_forbidden_tools(actual, forbidden)

    assert result["score"] == 1.0
    assert result["passed"] is True


def test_forbidden_tools_fail():
    actual = [
        "check_database",
        "check_service",
        "check_logs",
        "restart_service",
    ]

    forbidden = [
        "restart_service",
        "create_incident",
    ]

    result = score_forbidden_tools(actual, forbidden)

    assert result["score"] == 0.0
    assert result["passed"] is False
    assert "restart_service" in result["reason"]