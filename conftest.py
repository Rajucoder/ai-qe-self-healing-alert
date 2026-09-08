from dataclasses import replace
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config.settings import settings
from app.main import app


PROJECT_ROOT = Path(__file__).resolve().parent
TEST_DATA_FILE = PROJECT_ROOT / "test_data" / "agent_test_cases.json"


def load_test_cases():
    """Load the golden test scenarios from JSON."""
    with TEST_DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


@pytest.fixture
def test_cases():
    """Provide all golden test scenarios."""
    return load_test_cases()


@pytest.fixture
def api_client(test_case, monkeypatch):
    """
    Create a FastAPI test client configured for the current scenario.

    Each test gets its own simulated environment configuration.
    """
    scenario_environment = test_case["environment"]

    scenario_settings = replace(
        settings,
        sim_database_healthy=scenario_environment["database_healthy"],
        sim_service_healthy=scenario_environment["service_healthy"],
        sim_logs_normal=scenario_environment["logs_normal"],
        sim_restart_succeeds=scenario_environment["restart_succeeds"],
        sim_validation_healthy=scenario_environment["validation_healthy"],
    )

    monkeypatch.setattr("app.main.settings", scenario_settings)

    with TestClient(app) as client:
        yield client