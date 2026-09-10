from pathlib import Path

from app.retrieval.chunker import TextChunker
from app.retrieval.document_loader import DocumentLoader
from app.retrieval.embeddings import EmbeddingService
from app.retrieval.retriever import Retriever
from app.retrieval.vector_store import VectorStore


KNOWLEDGE_DIR = Path("knowledge")


def build_retriever():
    loader = DocumentLoader()
    chunker = TextChunker(
        chunk_size=40,
        overlap=10,
    )

    embedding_service = EmbeddingService()

    # all-MiniLM-L6-v2 produces 384-dimensional embeddings.
    vector_store = VectorStore(dimension=384)

    retriever = Retriever(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    documents = loader.load_directory(
        str(KNOWLEDGE_DIR)
    )

    all_chunks = []

    for document in documents:
        chunks = chunker.split(
            text=document["text"],
            source=document["source"],
        )

        all_chunks.extend(chunks)

    retriever.index_chunks(all_chunks)

    return retriever


def test_semantic_retrieval_returns_relevant_document():
    retriever = build_retriever()

    results = retriever.search(
        query="What should I verify before restarting the payment service?",
        top_k=3,
    )

    for chunk, score in results:
        print(
            f"\nScore: {score:.4f}"
            f"\nSource: {chunk.source}"
            f"\nChunk ID: {chunk.chunk_id}"
            f"\nText: {chunk.text}"
        )

    assert len(results) == 3

    sources = [chunk.source for chunk, score in results]

    assert (
        "service_health.md" in sources
        or "remediation_policy.md" in sources
    )

def test_top_k_limits_number_of_results():
    retriever = build_retriever()

    results = retriever.search(
        query="service health",
        top_k=2,
    )

    assert len(results) == 2

import pytest


def test_empty_query_is_rejected():
    retriever = build_retriever()

    with pytest.raises(ValueError):
        retriever.search(
            query="   ",
            top_k=3,
        )

def test_top_result_contains_expected_remediation_evidence():
    retriever = build_retriever()

    results = retriever.search(
        query="What should I verify before restarting the payment service?",
        top_k=3,
    )

    top_chunk, top_score = results[0]

    assert top_chunk.source == "remediation_policy.md"

    assert (
        "verify the service health and its dependencies"
        in top_chunk.text.lower()
    )

    assert top_score > 0.50