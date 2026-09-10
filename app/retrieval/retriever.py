from app.retrieval.chunker import DocumentChunk
from app.retrieval.embeddings import EmbeddingService
from app.retrieval.vector_store import VectorStore


class Retriever:
    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: VectorStore,
    ):
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    def index_chunks(self, chunks: list[DocumentChunk]) -> None:
        if not chunks:
            return

        texts = [chunk.text for chunk in chunks]

        embeddings = self.embedding_service.embed_texts(texts)

        self.vector_store.add(
            chunks=chunks,
            embeddings=embeddings,
        )

    def search(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[tuple[DocumentChunk, float]]:

        if not query.strip():
            raise ValueError("query must not be empty")

        query_embedding = self.embedding_service.embed_text(query)

        return self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
        )