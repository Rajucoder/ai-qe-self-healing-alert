from typing import Literal

from pydantic import BaseModel


class AgentInvokeResponse(BaseModel):
    status: Literal["resolved", "escalated", "no_action"]
    message: str
    incident_id: str | None
    service: str
    remediation_performed: bool


class ErrorResponse(BaseModel):
    error: str
    detail: str
