from pydantic import BaseModel, Field


class AgentInvokeRequest(BaseModel):
    alert: str = Field(min_length=1, max_length=2000)
    environment: str = Field(default="test", min_length=1, max_length=100)
    correlation_id: str | None = Field(default=None, min_length=1, max_length=200)
