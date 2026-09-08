from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.agent.agent import AuthorizedToolRegistry, SelfHealingAgent
from app.agent.provider import build_provider
from app.config.settings import settings
from app.models.requests import AgentInvokeRequest
from app.models.responses import AgentInvokeResponse, ErrorResponse
from app.tools.environment import SimulatedEnvironment
from app.tracing.mlflow_config import configure_mlflow

logging.basicConfig(level=settings.log_level, format="%(asctime)s %(levelname)s %(name)s %(message)s")


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_mlflow(settings)
    yield


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(error="validation_error", detail=str(exc)).model_dump(),
    )


@app.exception_handler(ValueError)
async def value_error_handler(_: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(error="configuration_error", detail=str(exc)).model_dump(),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error="request_error", detail=str(exc.detail)).model_dump(),
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


@app.post("/agent/invoke", response_model=AgentInvokeResponse)
def invoke_agent(request: AgentInvokeRequest) -> AgentInvokeResponse:
    if request.environment != "test":
        raise HTTPException(status_code=400, detail="Only the simulated 'test' environment is available.")
    environment = SimulatedEnvironment.from_settings(settings)
    agent = SelfHealingAgent(build_provider(settings))
    tools = AuthorizedToolRegistry(environment)
    return agent.invoke(request.alert, request.environment, tools, request.correlation_id)
