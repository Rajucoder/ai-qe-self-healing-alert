from app.retrieval.embeddings import EmbeddingService


def test_embedding_is_generated():
    service = EmbeddingService()

    vector = service.embed_text(
        "The payment service is unavailable."
    )

    assert vector is not None
    assert len(vector) > 0


def test_semantically_similar_text_has_high_similarity():
    service = EmbeddingService()

    vector_a = service.embed_text(
        "The payment service is unavailable."
    )

    vector_b = service.embed_text(
        "The payment API is down."
    )

    similarity = service.cosine_similarity(vector_a, vector_b)

    print(f"\nSemantic similarity: {similarity:.4f}")

    assert similarity > 0.5

def test_unrelated_text_has_lower_similarity():
    service = EmbeddingService()

    vector_a = service.embed_text(
        "The payment service is unavailable."
    )

    vector_b = service.embed_text(
        "The employee applied for leave."
    )

    similarity = service.cosine_similarity(vector_a, vector_b)

    print(f"\nUnrelated similarity: {similarity:.4f}")

    assert similarity < 0.5