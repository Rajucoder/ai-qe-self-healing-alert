from pathlib import Path

from app.retrieval.document_loader import DocumentLoader


KNOWLEDGE_DIR = Path("knowledge")


def test_load_single_document():
    loader = DocumentLoader()

    document = loader.load(
        str(KNOWLEDGE_DIR / "service_health.md")
    )

    assert document["text"]
    assert document["source"] == "service_health.md"


def test_load_all_knowledge_documents():
    loader = DocumentLoader()

    documents = loader.load_directory(
        str(KNOWLEDGE_DIR)
    )

    assert len(documents) == 3

    sources = {document["source"] for document in documents}

    assert sources == {
        "service_health.md",
        "remediation_policy.md",
        "incident_response.md",
    }