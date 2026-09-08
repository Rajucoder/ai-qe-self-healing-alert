from evaluation.llm_response_scorers import score_forbidden_claim
from evaluation.quality_gate import evaluate_quality_gate
from utils.trace_utils import find_trace_by_correlation_id


def test_real_groq_response_forbidden_claim_quality_gate():
    correlation_id = "day6-real-llm-001"

    trace = find_trace_by_correlation_id(correlation_id)

    assert trace is not None, (
        f"No MLflow trace found for correlation ID: {correlation_id}"
    )

    llm_spans = [
        span
        for span in trace.search_spans()
        if span.name == "groq_llm_call"
    ]

    assert llm_spans, "No Groq LLM span found in MLflow trace."

    llm_span = llm_spans[0]

    response = llm_span.outputs

    result = score_forbidden_claim(
        response,
        "lack of access to diagnostic tools",
    )

    result["required"] = True
    result["threshold"] = 1.0

    gate = evaluate_quality_gate([result])

    assert gate["status"] == "FAIL"
    assert gate["failed_required_scorers"] == 1