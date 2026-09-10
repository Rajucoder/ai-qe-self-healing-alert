import numpy as np
import pytest

from app.retrieval.chunker import DocumentChunk
from app.retrieval.vector_store import VectorStore


def create_chunk(text: str, chunk_id: str) -> DocumentChunk:
    return DocumentChunk(
        text=text,
        source="test.md",
        chunk_id=chunk_id,
        metadata={
            "source": "test.md",
            "chunk_id": chunk_id,
        },
    )


def test_vectors_can_be_added_and_searched():
    store = VectorStore(dimension=3)

    chunks = [
        create_chunk(
            "payment service is unavailable",
            "chunk-1",
        ),
        create_chunk(
            "employee applied for leave",
            "chunk-2",
        ),
    ]

    embeddings = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
        ],
        dtype="float32",
    )

    store.add(chunks, embeddings)

    results = store.search(
        query_embedding=np.array(
            [1.0, 0.0, 0.0],
            dtype="float32",
        ),
        top_k=1,
    )

    assert len(results) == 1
    assert results[0][0].chunk_id == "chunk-1"
    assert results[0][1] > 0.9

def test_empty_store_returns_no_results():
    store = VectorStore(dimension=3)

    results = store.search(
        query_embedding=np.array(
            [1.0, 0.0, 0.0],
            dtype="float32",
        ),
        top_k=3,
    )

    assert results == []

def test_top_k_must_be_positive():
    store = VectorStore(dimension=3)

    with pytest.raises(ValueError):
        store.search(
            query_embedding=np.array(
                [1.0, 0.0, 0.0],
                dtype="float32",
            ),
            top_k=0,
        )