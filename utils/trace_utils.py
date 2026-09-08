from __future__ import annotations

import time
from typing import Any

import mlflow

from app.config.settings import settings


def configure_mlflow() -> None:
    """Configure MLflow for trace retrieval."""
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment(settings.mlflow_experiment_name)


def find_trace_by_correlation_id(
    correlation_id: str, max_attempts: int = 10, wait_seconds: float = 0.5
) -> Any:
    """Find the exact trace tagged with ``correlation_id``, retrying briefly."""
    if not correlation_id:
        raise ValueError("correlation_id must be non-empty")

    configure_mlflow()
    escaped_id = correlation_id.replace("'", "''")
    filter_string = f"tag.correlation_id = '{escaped_id}'"

    for _ in range(max_attempts):
        traces = mlflow.search_traces(
            filter_string=filter_string,
            max_results=10,
            return_type="list",
            include_spans=True,
            flush=True,
        )
        if traces:
            return traces[0]

        time.sleep(wait_seconds)

    raise AssertionError(
        f"No MLflow trace found for correlation_id={correlation_id!r} "
        f"after {max_attempts} attempts"
    )


def find_trace_by_alert(alert: str, max_attempts: int = 10, wait_seconds: float = 0.5) -> Any:
    """Backward-compatible legacy lookup; new callers should use correlation IDs."""
    configure_mlflow()
    for _ in range(max_attempts):
        traces = mlflow.search_traces(
            filter_string="trace.status = 'OK'",
            order_by=["timestamp_ms DESC"],
            max_results=20,
            return_type="list",
            include_spans=True,
            flush=True,
        )
        for trace in traces:
            if alert in str(trace.data.request):
                return trace
        time.sleep(wait_seconds)
    raise AssertionError(f"No MLflow trace found for alert: {alert}")


def extract_tool_names(trace: Any) -> list[str]:
    """
    Extract tool span names from an MLflow trace
    in execution order.
    """

    if hasattr(trace, "data"):
        spans = trace.data.spans
        return [span.name for span in spans if str(span.span_type).strip('"') == "TOOL"]

    spans = trace["spans"]
    return [span["name"] for span in spans if span["attributes"].get("mlflow.spanType") == '"TOOL"']

def find_forbidden_tools(actual_tools, forbidden_tools):
    """Return any forbidden tools that were actually executed."""

    return [
        tool
        for tool in actual_tools
        if tool in forbidden_tools
    ]

def validate_tool_sequence(actual_tools, expected_tools):
    """Validate that tools were executed in the expected order."""

    return {
        "passed": actual_tools == expected_tools,
        "expected": expected_tools,
        "actual": actual_tools,
    }