import pytest

from app.retrieval.chunker import TextChunker


def test_document_is_split_into_chunks():
    text = " ".join(f"word{i}" for i in range(1, 26))

    chunker = TextChunker(
        chunk_size=10,
        overlap=2,
    )

    chunks = chunker.split(
        text=text,
        source="test_document.md",
    )

    assert len(chunks) == 3

def test_chunk_metadata_is_preserved():
    text = "The payment service depends on the database."

    chunker = TextChunker(
        chunk_size=10,
        overlap=2,
    )

    chunks = chunker.split(
        text=text,
        source="service_health.md",
    )

    assert chunks[0].source == "service_health.md"
    assert chunks[0].chunk_id == "service_health.md-chunk-1"
    assert chunks[0].text == text

def test_overlap_must_be_smaller_than_chunk_size():
    with pytest.raises(ValueError):
        TextChunker(
            chunk_size=10,
            overlap=10,
        )

def test_chunk_metadata_is_available():
    text = "The payment service depends on the database."

    chunker = TextChunker(
        chunk_size=10,
        overlap=2,
    )

    chunks = chunker.split(
        text=text,
        source="service_health.md",
    )

    metadata = chunks[0].metadata

    assert metadata["source"] == "service_health.md"
    assert metadata["chunk_id"] == "service_health.md-chunk-1"