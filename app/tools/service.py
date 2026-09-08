from __future__ import annotations

import mlflow

from app.tools.environment import SimulatedEnvironment


@mlflow.trace(name="check_service", span_type="TOOL")
def check_service(service_name: str, environment: SimulatedEnvironment) -> dict[str, object]:
    return {
        "service": service_name,
        "healthy": environment.service_healthy,
        "source": "simulated",
    }


@mlflow.trace(name="restart_service", span_type="TOOL")
def restart_service(
    service_name: str, reason: str, environment: SimulatedEnvironment
) -> dict[str, object]:
    succeeded = environment.restart_succeeds
    if succeeded:
        environment.service_healthy = True
    return {
        "service": service_name,
        "succeeded": succeeded,
        "simulated": True,
        "reason": reason,
    }


@mlflow.trace(name="validate_service", span_type="TOOL")
def validate_service(service_name: str, environment: SimulatedEnvironment) -> dict[str, object]:
    healthy = environment.validation_healthy and environment.service_healthy
    return {"service": service_name, "healthy": healthy, "source": "simulated"}
