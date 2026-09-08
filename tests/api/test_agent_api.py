import json
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEST_DATA_FILE = PROJECT_ROOT / "test_data" / "agent_test_cases.json"


def load_test_cases():
    """Load golden test scenarios from JSON."""
    with TEST_DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


TEST_CASES = load_test_cases()


@pytest.mark.parametrize(
    "test_case",
    TEST_CASES,
    ids=lambda case: case["id"],
)
def test_agent_response_matches_expected(test_case, api_client):
    """Verify the API response matches the expected scenario outcome."""

    response = api_client.post(
        "/agent/invoke",
        json=test_case["request"],
    )

    assert response.status_code == 200

    response_data = response.json()
    expected = test_case["expected"]

    assert response_data["status"] == expected["status"]
    assert (
        response_data["remediation_performed"]
        == expected["remediation_performed"]
    )

    if expected["incident_created"]:
        assert response_data["incident_id"] is not None
    else:
        assert response_data["incident_id"] is None