from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class IncidentStatus(StrEnum):
    INVESTIGATING = "investigating"
    REMEDIATING = "remediating"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    NO_ACTION = "no_action"


@dataclass
class AgentState:
    alert: str
    environment: str
    service: str = ""
    status: IncidentStatus = IncidentStatus.INVESTIGATING
    database_healthy: bool | None = None
    service_healthy: bool | None = None
    logs_normal: bool | None = None
    remediation_performed: bool = False
    validation_healthy: bool | None = None
    incident_id: str | None = None
    events: list[dict[str, Any]] = field(default_factory=list)

    def record(self, event: str, **details: Any) -> None:
        self.events.append({"event": event, **details})
