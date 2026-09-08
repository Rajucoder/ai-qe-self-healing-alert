from uuid import uuid4

import pytest

from evaluation.quality_gate import evaluate_quality_gate
from evaluation.trajectory_scorers import (
    score_forbidden_tools,
    score_tool_trajectory,
)
from utils.trace_utils import (
    extract_tool_names,
    find_trace_by_correlation_id,
)

@pytest.mark.parametrize(
    "test_case",
    __import__("json").load(
        open("test_data/agent_test_cases.json", encoding="utf-8")
    ),
    ids=lambda case: case["id"],
)
def test_agent_tool_trajectory(test_case, api_client):
    """Verify the agent follows the expected tool trajectory."""

    correlation_id = (
        f"pytest-{test_case['id']}-{uuid4().hex}"
    )

    request_payload = {
        **test_case["request"],
        "correlation_id": correlation_id,
    }

    response = api_client.post(
        "/agent/invoke",
        json=request_payload,
    )

    assert response.status_code == 200

    trace = find_trace_by_correlation_id(
        correlation_id
    )

    actual_tools = extract_tool_names(trace)

    expected_tools = test_case["expected"]["trajectory"]

    trajectory_result = score_tool_trajectory(
        actual_tools,
        expected_tools,
    )

    trajectory_result["required"] = 1.0

    forbidden_tools = test_case["expected"].get(
        "forbidden_tools",
        []
    )

    forbidden_result = score_forbidden_tools(
        actual_tools,
        forbidden_tools,
    )

    forbidden_result["required"] = 1.0

    scorer_results = [
        trajectory_result,
        forbidden_result,
    ]

    quality_gate_result = evaluate_quality_gate(
        scorer_results
    )

    assert quality_gate_result["status"] == "PASS", (
        f"Quality gate failed.\n"
        f"Scenario: {test_case['id']}\n"
        f"Correlation ID: {correlation_id}\n"
        f"Failed scorers: "
        f"{quality_gate_result['failed_results']}"
    )

