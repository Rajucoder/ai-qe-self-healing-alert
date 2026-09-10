import faiss
import numpy as np

from app.retrieval.chunker import DocumentChunk


class VectorStore:
    def __init__(self, dimension: int):
        self.dimension = dimension

        # Inner-product index.
        # We will store normalized vectors, making this equivalent
        # to cosine similarity.
        self.index = faiss.IndexFlatIP(dimension)

        # Keep the original chunks alongside the FAISS index.
        self.chunks: list[DocumentChunk] = []

    def add(
        self,
        chunks: list[DocumentChunk],
        embeddings,
    ) -> None:

        if len(chunks) != len(embeddings):
            raise ValueError(
                "Number of chunks must match number of embeddings"
            )

        vectors = np.asarray(
            embeddings,
            dtype="float32",
        )

        if vectors.ndim != 2:
            raise ValueError(
                "Embeddings must be a 2-dimensional array"
            )

        if vectors.shape[1] != self.dimension:
            raise ValueError(
                "Embedding dimension does not match vector store"
            )

        # Normalize vectors so inner product = cosine similarity.
        faiss.normalize_L2(vectors)

        self.index.add(vectors)
        self.chunks.extend(chunks)

    def search(
        self,
        query_embedding,
        top_k: int = 3,
    ) -> list[tuple[DocumentChunk, float]]:

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero")

        if self.index.ntotal == 0:
            return []

        query_vector = np.asarray(
            [query_embedding],
            dtype="float32",
        )

        if query_vector.shape[1] != self.dimension:
            raise ValueError(
                "Query embedding dimension does not match vector store"
            )

        faiss.normalize_L2(query_vector)

        scores, indices = self.index.search(
            query_vector,
            min(top_k, self.index.ntotal),
        )

        results = []

        for score, index in zip(scores[0], indices[0]):
            if index == -1:
                continue

            results.append(
                (
                    self.chunks[index],
                    float(score),
                )
            )

        return results