from openai import OpenAI
from ragas.llms import llm_factory
from ragas.metrics import Faithfulness
from datasets import Dataset
from ragas import evaluate

from app.agent.provider import GroqProvider
from app.config.settings import settings
from app.retrieval.chunker import TextChunker
from app.retrieval.document_loader import DocumentLoader
from app.retrieval.embeddings import EmbeddingService
from app.retrieval.retriever import Retriever
from app.retrieval.vector_store import VectorStore
from app.rag.rag_service import RagService


def build_rag():
    """
    Build the existing RAG application.

    This is the same RAG pipeline used during Day 9:
    documents -> chunks -> embeddings -> vector store
    -> retriever -> RAG service
    """

    embedding_service = EmbeddingService()

    loader = DocumentLoader()

    documents = loader.load_directory("knowledge")

    chunker = TextChunker()

    chunks = []

    for document in documents:
        chunks.extend(
            chunker.split(
                text=document["text"],
                source=document["source"],
            )
        )

    vector_store = VectorStore(dimension=384)

    retriever = Retriever(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    retriever.index_chunks(chunks)

    provider = GroqProvider(settings)

    return RagService(
        retriever=retriever,
        provider=provider,
    )


def main():

    # ============================================================
    # 1. RAGAS EVALUATOR LLM
    # ============================================================

    client = OpenAI(
        api_key=settings.groq_api_key,
        base_url="https://api.groq.com/openai/v1",
    )

    evaluator_llm = llm_factory(
        model=settings.groq_model,
        provider="openai",
        client=client,
        multiple_completion_supported=False,
    )

    faithfulness = Faithfulness(
        llm=evaluator_llm
    )

    # ============================================================
    # 2. BUILD EXISTING RAG APPLICATION
    # ============================================================

    rag = build_rag()

    question = (
        "What should I verify before restarting "
        "the payment service?"
    )

    # ============================================================
    # 3. RETRIEVE CONTEXT
    # ============================================================

    results = rag.retriever.search(
        query=question,
        top_k=3,
    )

    contexts = [
        chunk.text
        for chunk, score in results
    ]

    # ============================================================
    # 4. GENERATE RAG ANSWER
    # ============================================================

    answer = rag.answer(question)

    print("\n" + "=" * 70)
    print("RAGAS FAITHFULNESS EVALUATION")
    print("=" * 70)

    print("\nQuestion:")
    print(question)

    print("\nAnswer:")
    print(answer)

    print("\nRetrieved Contexts:")

    for index, context in enumerate(contexts, start=1):
        print(f"\n--- Context {index} ---")
        print(context)

    # ============================================================
    # 5. CREATE RAGAS DATASET
    # ============================================================

    dataset = Dataset.from_dict(
        {
            "user_input": [question],
            "response": [answer],
            "retrieved_contexts": [contexts],
        }
    )

    # ============================================================
    # 6. RUN RAGAS
    # ============================================================

    print("\nRunning RAGAS evaluate()...")

    result = evaluate(
        dataset=dataset,
        metrics=[faithfulness],
        raise_exceptions=True,
        show_progress=True,
    )

    # ============================================================
    # 7. DISPLAY RESULT
    # ============================================================

    print("\n" + "=" * 70)
    print("RAGAS RESULT")
    print("=" * 70)

    print(result)

    print("\nFaithfulness score:")

    print(result["faithfulness"])

    print("=" * 70)


if __name__ == "__main__":
    main()