from __future__ import annotations

import mlflow

from app.tools.environment import SimulatedEnvironment


@mlflow.trace(name="check_database", span_type="TOOL")
def check_database(database_name: str, environment: SimulatedEnvironment) -> dict[str, object]:
    return {
        "database": database_name,
        "healthy": environment.database_healthy,
        "source": "simulated",
    }
