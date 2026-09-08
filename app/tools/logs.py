from __future__ import annotations

import mlflow

from app.tools.environment import SimulatedEnvironment


@mlflow.trace(name="check_logs", span_type="TOOL")
def check_logs(
    service_name: str,
    environment: SimulatedEnvironment,
    time_window: str | None = None,
) -> dict[str, object]:
    entries = [
        "No relevant errors detected in simulated logs."
        if environment.logs_normal
        else "ERROR request failures detected in simulated logs."
    ]
    return {
        "service": service_name,
        "time_window": time_window or "15m",
        "normal": environment.logs_normal,
        "entries": entries,
        "source": "simulated",
    }
