# ai-qe-self-healing-agent

A deterministic, observable FastAPI application that investigates operational alerts and performs only safe simulated remediation. It is the application under test; no QA framework or test suite is included.

## Architecture

`POST /agent/invoke` creates a fresh `SimulatedEnvironment`, an `AuthorizedToolRegistry`, and a typed `SelfHealingAgent`. The agent identifies the service, checks the database, service, and logs, decides whether remediation is needed, simulates a restart, validates the service, and escalates through a simulated incident when recovery fails.

All state is explicit in `AgentState`. The registry is an allowlist of exactly six tools. The tools never access a host, process, database, container, Kubernetes cluster, or production system. The default LLM provider is deterministic; OpenAI is an optional provider behind the same protocol.

## Install

```powershell
cd ai-qe-self-healing-agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and change values as needed. `.env` is ignored by git.

## Environment variables

`MLFLOW_TRACKING_URI` defaults to `http://localhost:5000`. `MLFLOW_EXPERIMENT_NAME` selects the MLflow experiment. `LLM_PROVIDER` is `deterministic` by default or `openai`; the latter requires `OPENAI_API_KEY` and optionally `OPENAI_MODEL`.

The deterministic state is controlled by `SIM_DATABASE_HEALTHY`, `SIM_SERVICE_HEALTHY`, `SIM_LOGS_NORMAL`, `SIM_RESTART_SUCCEEDS`, and `SIM_VALIDATION_HEALTHY`. Set them to `true` or `false` before starting the app. A new environment is created for every invocation, so scenarios are isolated and repeatable.

## Start MLflow locally

With MLflow installed, run:

```powershell
mlflow server --host 0.0.0.0 --port 5000
```

For a local file-backed development setup without a server, set `MLFLOW_TRACKING_URI=mlruns`; the example configuration uses the local server instead.

## Start the API

```powershell
uvicorn app.main:app --reload --port 8000
```

## Example requests

```powershell
curl http://localhost:8000/health
```

```powershell
curl -X POST http://localhost:8000/agent/invoke `
  -H "Content-Type: application/json" `
  -d '{"alert":"Order service is unavailable","environment":"test"}'
```

A healthy scenario returns `no_action`. An unhealthy service with a successful simulated restart returns `resolved`; failed validation or an unhealthy database returns `escalated` with a deterministic simulated incident ID.

## MLflow traces

The root `self_healing_agent` function is decorated with the current `@mlflow.trace` API. Nested traced functions record the LLM call and every authorized tool call, including their inputs and outputs. The root trace is tagged with status and service and stores the explicit state events as metadata. Open the configured experiment in the MLflow UI after invoking the API.

## Limitations and assumptions

The service name extractor intentionally supports simple alert phrasing and defaults to `order service`. Environment values are loaded at process startup, so restart the API after changing `.env`. The deterministic provider does not make a network call; the optional OpenAI provider is only used when explicitly selected. This project intentionally has no automated test suite yet.
