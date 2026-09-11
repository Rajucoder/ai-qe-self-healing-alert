# AI-QE Self-Healing Agent

A simulated self-healing incident-response agent built as a FastAPI service. It accepts an alert, investigates service health and dependencies, decides whether remediation is needed, and records its actions in MLflow traces. All actions are intentionally limited to a small allowlist of tools so the system can be evaluated safely without touching real production systems.

## What this project does

- Exposes a FastAPI endpoint for agent evaluation: `POST /agent/invoke`
- Creates a fresh simulated environment for each request
- Verifies service health, database health, and logs
- Performs a simulated restart when needed
- Validates the service after remediation
- Escalates a simulated incident if recovery fails
- Records trace metadata in MLflow
- Supports Promptfoo-based testing against the running API

## Architecture

The app is intentionally simple and observable:

- `app/main.py` exposes the FastAPI service
- `app/agent/agent.py` contains the `SelfHealingAgent`
- `app/tools/*` defines the allowed tools and simulation behavior
- `app/tracing/mlflow_config.py` configures MLflow tracing
- `promptfooconfig.yaml` defines end-to-end evaluation cases against the API
- `tests/` contains project-level validation and regression checks

## Tech stack

- Python
- FastAPI
- Pydantic
- MLflow
- Promptfoo
- Pytest

## Prerequisites

- Python 3.10+
- A local MLflow server
- Optional: Groq/OpenAI credentials if you want to use a real LLM provider

## Setup

```bash
cd ai-qe-self-healing-agent
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# or .\.venv\Scripts\Activate.ps1   # Windows PowerShell
pip install -r requirements.txt
```

Copy the sample environment file and adjust values if needed:

```bash
cp .env.example .env
```

The project reads configuration from environment variables such as:

- `MLFLOW_TRACKING_URI`
- `MLFLOW_EXPERIMENT_NAME`
- `LLM_PROVIDER`
- `GROQ_API_KEY`
- `SIM_DATABASE_HEALTHY`
- `SIM_SERVICE_HEALTHY`
- `SIM_LOGS_NORMAL`
- `SIM_RESTART_SUCCEEDS`
- `SIM_VALIDATION_HEALTHY`

## Start MLflow

```bash
mlflow server --host 0.0.0.0 --port 5000
```

Then set the environment variable if needed:

```bash
export MLFLOW_TRACKING_URI=http://localhost:5000
```

## Start the API

```bash
uvicorn app.main:app --reload --port 8000
```

## Health check

```bash
curl http://localhost:8000/health
```

Example response:

```json
{"status": "ok", "service": "ai-qe-self-healing-agent"}
```

## Example agent request

```bash
curl -X POST http://localhost:8000/agent/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "alert": "The payment service is unhealthy.",
    "environment": "test",
    "correlation_id": "demo-001"
  }'
```

Example response shape:

```json
{
  "status": "no_action",
  "message": "No remediation required; service and dependencies are healthy.",
  "incident_id": null,
  "service": "payment service",
  "remediation_performed": false
}
```

Status values include:

- `no_action`
- `resolved`
- `escalated`

## Promptfoo evaluation

This project includes a Promptfoo configuration at `promptfooconfig.yaml` that calls the live FastAPI endpoint and validates assertions against the returned JSON.

To run Promptfoo:

```bash
npx promptfoo eval
```

The configuration includes:

- deterministic JavaScript assertions against API output
- a malicious prompt-injection regression case
- a rubric-based LLM judge using Groq/OpenAI-compatible models

## MLflow traces

The root agent invocation is traced with MLflow. Each request records investigation steps, tool calls, and final state transitions, making it easy to inspect the decision path in the MLflow UI.

## Safety model

This project intentionally simulates all system actions and never interacts with real infrastructure. The tool registry is allowlisted and only supports safe simulated tools such as:

- checking service health
- checking database health
- checking logs
- restarting a simulated service
- validating service health
- creating a simulated incident

## Project structure

```text
ai-qe-self-healing-agent/
├── app/
│   ├── agent/
│   ├── config/
│   ├── models/
│   ├── tools/
│   ├── tracing/
│   └── main.py
├── evaluation/
├── prompts/
├── tests/
├── .env.example
├── promptfooconfig.yaml
├── pyproject.toml
├── requirements.txt
├── README.md
└── Dockerfile
```

## Notes

- The service name extraction is intentionally simple and may default to `order service` for generic alerts.
- New simulated scenarios are isolated by creating a fresh environment for each API invocation.
- The deterministic provider is the default path; a real LLM provider is only used when configured explicitly.
