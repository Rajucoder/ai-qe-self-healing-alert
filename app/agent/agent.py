from __future__ import annotations

import logging
import re
from typing import Callable

import mlflow

from app.agent.prompts import SYSTEM_PROMPT
from app.agent.provider import LLMProvider
from app.agent.state import AgentState, IncidentStatus
from app.models.responses import AgentInvokeResponse
from app.tools.database import check_database
from app.tools.environment import SimulatedEnvironment
from app.tools.incident import create_incident
from app.tools.logs import check_logs
from app.tools.service import check_service, restart_service, validate_service

logger = logging.getLogger(__name__)


class AuthorizedToolRegistry:
    def __init__(self, environment: SimulatedEnvironment) -> None:
        self.environment = environment
        self._tools: dict[str, Callable[..., dict[str, object]]] = {
            "check_database": self._check_database,
            "check_service": self._check_service,
            "check_logs": self._check_logs,
            "restart_service": self._restart_service,
            "validate_service": self._validate_service,
            "create_incident": self._create_incident,
        }

    @property
    def allowed_tools(self) -> tuple[str, ...]:
        return tuple(self._tools)

    def call(self, name: str, **kwargs: object) -> dict[str, object]:
        if name not in self._tools:
            raise PermissionError(f"Tool is not authorized: {name}")
        return self._tools[name](**kwargs)

    def _check_database(self, database_name: str) -> dict[str, object]:
        return check_database(database_name, self.environment)

    def _check_service(self, service_name: str) -> dict[str, object]:
        return check_service(service_name, self.environment)

    def _check_logs(self, service_name: str, time_window: str | None = None) -> dict[str, object]:
        return check_logs(service_name, self.environment, time_window)

    def _restart_service(self, service_name: str, reason: str) -> dict[str, object]:
        return restart_service(service_name, reason, self.environment)

    def _validate_service(self, service_name: str) -> dict[str, object]:
        return validate_service(service_name, self.environment)

    def _create_incident(self, service_name: str, reason: str, severity: str) -> dict[str, object]:
        return create_incident(service_name, reason, severity)


class SelfHealingAgent:
    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider

    @mlflow.trace(name="self_healing_agent", span_type="CHAIN")
    def invoke(
        self,
        alert: str,
        environment: str,
        tools: AuthorizedToolRegistry,
        correlation_id: str | None = None,
    ) -> AgentInvokeResponse:
        state = AgentState(alert=alert, environment=environment)
        if correlation_id:
            mlflow.update_current_trace(tags={"correlation_id": correlation_id})
            state.record("correlation_id_assigned", correlation_id=correlation_id)
        state.service = self._identify_service(alert)
        state.record("service_identified", service=state.service)
        llm_response = self.provider.complete(SYSTEM_PROMPT, f"Alert: {alert}\nService: {state.service}")

        state.record("llm_response_received", response=llm_response,)

        database = tools.call("check_database", database_name="orders-db")
        service = tools.call("check_service", service_name=state.service)
        logs = tools.call("check_logs", service_name=state.service, time_window="15m")
        state.database_healthy = bool(database["healthy"])
        state.service_healthy = bool(service["healthy"])
        state.logs_normal = bool(logs["normal"])
        state.record("investigation_complete", database=database, service=service, logs=logs)

        if state.service_healthy and state.database_healthy and state.logs_normal:
            state.status = IncidentStatus.NO_ACTION
            return self._response(state, "No remediation required; service and dependencies are healthy.")

        state.status = IncidentStatus.REMEDIATING
        state.record("remediation_decision", required=True)
        restart = tools.call(
            "restart_service",
            service_name=state.service,
            reason="Service health check failed during alert investigation.",
        )
        state.remediation_performed = True
        state.record("remediation_complete", result=restart)
        validation = tools.call("validate_service", service_name=state.service)
        state.validation_healthy = bool(validation["healthy"])
        state.record("validation_complete", result=validation)

        if state.validation_healthy and state.database_healthy:
            state.status = IncidentStatus.RESOLVED
            return self._response(state, "Service remediation succeeded and validation is healthy.")

        state.status = IncidentStatus.ESCALATED
        incident = tools.call(
            "create_incident",
            service_name=state.service,
            reason="Automated remediation did not restore a healthy service or dependency.",
            severity="high",
        )
        state.incident_id = str(incident["incident_id"])
        state.record("escalation_complete", incident=incident)
        return self._response(state, "Remediation did not restore health; incident escalated.")

    @staticmethod
    def _identify_service(alert: str) -> str:
        match = re.search(r"([a-z][a-z0-9-]*\s+service)", alert.lower())
        if match:
            return match.group(1)
        return "order service"

    @staticmethod
    def _response(state: AgentState, message: str) -> AgentInvokeResponse:
        logger.info("Agent invocation completed", extra={"status": state.status.value, "service": state.service})
        mlflow.update_current_trace(
            tags={"status": state.status.value, "service": state.service},
            metadata={"events": state.events},
            response_preview=message,
        )
        return AgentInvokeResponse(
            status=state.status.value,
            message=message,
            incident_id=state.incident_id,
            service=state.service,
            remediation_performed=state.remediation_performed,
        )
