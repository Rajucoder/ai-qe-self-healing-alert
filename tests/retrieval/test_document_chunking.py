from pathlib import Path

from app.retrieval.chunker import TextChunker
from app.retrieval.document_loader import DocumentLoader


KNOWLEDGE_DIR = Path("knowledge")


def test_loaded_document_can_be_chunked():
    loader = DocumentLoader()
    chunker = TextChunker(
        chunk_size=40,
        overlap=10,
    )

    document = loader.load(
        str(KNOWLEDGE_DIR / "service_health.md")
    )

    chunks = chunker.split(
        text=document["text"],
        source=document["source"],
    )

    assert len(chunks) > 1

    assert all(chunk.text for chunk in chunks)

    assert all(
        chunk.source == "service_health.md"
        for chunk in chunks
    )

    assert chunks[0].chunk_id == "service_health.md-chunk-1"