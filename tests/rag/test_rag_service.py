from pathlib import Path

from app.agent.provider import GroqProvider
from app.config.settings import settings
from app.rag.rag_service import RagService
from app.retrieval.chunker import TextChunker
from app.retrieval.document_loader import DocumentLoader
from app.retrieval.embeddings import EmbeddingService
from app.retrieval.retriever import Retriever
from app.retrieval.vector_store import VectorStore


def build_retriever():
    project_root = Path(__file__).resolve().parents[2]
    knowledge_dir = project_root / "knowledge"

    loader = DocumentLoader()
    documents = loader.load_directory(str(knowledge_dir))

    chunker = TextChunker(
        chunk_size=100,
        overlap=20,
    )

    chunks = []

    for document in documents:
        chunks.extend(
            chunker.split(
                text=document["text"],
                source=document["source"],
            )
        )

    embedding_service = EmbeddingService()

    vector_store = VectorStore(
        dimension=384,
    )

    retriever = Retriever(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    retriever.index_chunks(chunks)

    return retriever


def test_rag_pipeline_connects_retrieval_to_context_and_llm():
    retriever = build_retriever()

    provider = GroqProvider(settings)

    rag_service = RagService(
        retriever=retriever,
        provider=provider,
    )

    answer = rag_service.answer(
        query="What is the maximum number of retries allowed when restarting the payment service?",
        top_k=3,
    )

    assert answer

    print("\nRAG ANSWER:")
    print(answer)