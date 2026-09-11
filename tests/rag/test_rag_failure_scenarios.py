from app.agent.provider import DeterministicProvider
from app.rag.rag_service import RagService
from app.retrieval.chunker import DocumentChunk


class IrrelevantRetriever:
    def search(self, query: str, top_k: int = 3):
        irrelevant_chunk = DocumentChunk(
            text="The service is healthy when it is running and dependencies are available.",
            source="service_health.md",
            chunk_id="chunk_irrelevant",
            metadata={},
        )

        return [(irrelevant_chunk, 0.20)]


def test_rag_does_not_answer_from_irrelevant_context():
    retriever = IrrelevantRetriever()
    provider = DeterministicProvider()

    rag_service = RagService(
        retriever=retriever,
        provider=provider,
    )

    query = "What is the maximum number of retries allowed when restarting the payment service?"

    response = rag_service.answer(query)

    assert "maximum number of retries" not in response.lower()