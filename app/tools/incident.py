from __future__ import annotations

import hashlib

import mlflow


@mlflow.trace(name="create_incident", span_type="TOOL")
def create_incident(service_name: str, reason: str, severity: str) -> dict[str, str]:
    digest = hashlib.sha1(f"{service_name}|{reason}|{severity}".encode()).hexdigest()[:10].upper()
    return {
        "incident_id": f"SIM-{digest}",
        "service": service_name,
        "severity": severity,
        "simulated": "true",
    }
