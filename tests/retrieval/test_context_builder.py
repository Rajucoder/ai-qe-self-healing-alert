from app.retrieval.context_builder import ContextBuilder
from app.retrieval.chunker import DocumentChunk


def create_chunk(text, source, chunk_id):
    return DocumentChunk(
        text=text,
        source=source,
        chunk_id=chunk_id,
        metadata={
            "source": source,
            "chunk_id": chunk_id,
        },
    )


def test_context_builder_preserves_all_chunks():
    builder = ContextBuilder()

    chunk_1 = create_chunk(
        "Verify service health.",
        "remediation_policy.md",
        "remediation_policy.md-chunk-1",
    )

    chunk_2 = create_chunk(
        "Check database connectivity.",
        "service_health.md",
        "service_health.md-chunk-1",
    )

    results = [
        (chunk_1, 0.85),
        (chunk_2, 0.72),
    ]

    context = builder.build(results)

    assert "Verify service health." in context
    assert "Check database connectivity." in context


def test_context_builder_preserves_metadata():
    builder = ContextBuilder()

    chunk = create_chunk(
        "Verify service health.",
        "remediation_policy.md",
        "remediation_policy.md-chunk-1",
    )

    context = builder.build([(chunk, 0.85)])

    assert "remediation_policy.md" in context
    assert "remediation_policy.md-chunk-1" in context


def test_context_builder_preserves_order():
    builder = ContextBuilder()

    chunk_1 = create_chunk("FIRST evidence.", "doc1.md", "doc1-chunk-1")
    chunk_2 = create_chunk("SECOND evidence.", "doc2.md", "doc2-chunk-1")
    chunk_3 = create_chunk("THIRD evidence.", "doc3.md", "doc3-chunk-1")

    results = [
        (chunk_1, 0.90),
        (chunk_2, 0.80),
        (chunk_3, 0.70),
    ]

    context = builder.build(results)

    assert context.index("FIRST evidence.") < context.index("SECOND evidence.")
    assert context.index("SECOND evidence.") < context.index("THIRD evidence.")


def test_context_builder_handles_empty_results():
    builder = ContextBuilder()

    context = builder.build([])

    assert context == "No relevant context was retrieved."