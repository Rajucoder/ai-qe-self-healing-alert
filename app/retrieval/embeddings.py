from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_text(self, text: str):
        return self.model.encode(text)

    def embed_texts(self, texts: list[str]):
        return self.model.encode(texts)

    @staticmethod
    def cosine_similarity(vector_a, vector_b) -> float:
        return float(
            np.dot(vector_a, vector_b)
            / (np.linalg.norm(vector_a) * np.linalg.norm(vector_b))
        )