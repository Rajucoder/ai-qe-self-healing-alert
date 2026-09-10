from dataclasses import dataclass


@dataclass
class DocumentChunk:
    text: str
    source: str
    chunk_id: str
    metadata: dict


class TextChunker:
    def __init__(self, chunk_size: int = 100, overlap: int = 20):
        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")

        self.chunk_size = chunk_size
        self.overlap = overlap

    def split(
        self,
        text: str,
        source: str,
    ) -> list[DocumentChunk]:

        words = text.split()
        chunks = []

        start = 0
        chunk_number = 1

        while start < len(words):
            end = min(start + self.chunk_size, len(words))

            chunk_text = " ".join(words[start:end])

            chunk_id = f"{source}-chunk-{chunk_number}"

            chunks.append(
                DocumentChunk(
                    text=chunk_text,
                    source=source,
                    chunk_id=chunk_id,
                    metadata={
                        "source": source,
                        "chunk_id": chunk_id,
                    },
                )
            )

            if end == len(words):
                break

            start = end - self.overlap
            chunk_number += 1

        return chunks