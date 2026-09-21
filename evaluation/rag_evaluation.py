import json
from pathlib import Path

from app.agent.provider import GroqProvider
from app.config.settings import settings
from app.rag.rag_service import RagService
from app.retrieval.chunker import TextChunker
from app.retrieval.document_loader import DocumentLoader
from app.retrieval.embeddings import EmbeddingService
from app.retrieval.retriever import Retriever
from app.retrieval.vector_store import VectorStore
from evaluation.rag_deterministic_scorer import (
    score_abstention,
    score_expected_evidence,
)

DATASET_PATH = Path("test_data/rag_test_cases.json")
KNOWLEDGE_PATH = "knowledge"

EMBEDDING_DIMENSION = 384


def build_rag_service() -> RagService:
    # 1. Create embedding service
    embedding_service = EmbeddingService()

    # 2. Load knowledge documents
    loader = DocumentLoader()
    documents = loader.load_directory(KNOWLEDGE_PATH)

    # 3. Chunk documents
    chunker = TextChunker()

    chunks = []

    for document in documents:
        document_chunks = chunker.split(
            text=document["text"],
            source=document["source"],
        )

        chunks.extend(document_chunks)

    # 4. Create vector store
    vector_store = VectorStore(
        dimension=EMBEDDING_DIMENSION
    )

    # 5. Create retriever
    retriever = Retriever(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    # 6. Index chunks
    retriever.index_chunks(chunks)

    # 7. Create LLM provider
    provider = GroqProvider(settings)

    # 8. Create RAG service
    return RagService(
        retriever=retriever,
        provider=provider,
    )


def load_dataset():
    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def run_evaluation():
    dataset = load_dataset()

    rag_service = build_rag_service()

    results = []

    for scenario in dataset:
        print("\n" + "=" * 70)
        print(f"Scenario: {scenario['id']}")
        print(f"Question: {scenario['question']}")

        answer = rag_service.answer(
            scenario["question"],
            top_k=3,
        )

        evidence_result = score_expected_evidence(
            answer,
            scenario["expected_evidence"],
        )

        abstention_result = score_abstention(
            answer,
            scenario["expected_evidence"],
        )

        passed = (
            evidence_result["passed"]
            and abstention_result["passed"]
        )

        print("\nEvaluation:")
        print(f"  Evidence score: {evidence_result['score']}")
        print(f"  Abstention score: {abstention_result['score']}")
        print(f"  Overall: {'PASS' if passed else 'FAIL'}")
        print("\nAnswer:")
        print(answer)

        results.append(
            {
                "id": scenario["id"],
                "question": scenario["question"],
                "answer": answer,
                "expected_evidence": scenario["expected_evidence"],
                "expected_behavior": scenario["expected_behavior"],
                "evidence_score": evidence_result["score"],
                "abstention_score": abstention_result["score"],
                "passed": passed,
            }
        )

    return results


if __name__ == "__main__":
    run_evaluation()