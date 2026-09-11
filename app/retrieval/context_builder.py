class ContextBuilder:
    def build(self, results):
        if not results:
            return "No relevant context was retrieved."

        sections = []

        for chunk, score in results:
            sections.append(
                f"--- Source: {chunk.source} | "
                f"Chunk: {chunk.chunk_id} | "
                f"Score: {score:.4f} ---\n"
                f"{chunk.text}"
            )

        return "\n\n".join(sections)