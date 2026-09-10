from pathlib import Path


class DocumentLoader:
    def load(self, file_path: str) -> dict:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")

        text = path.read_text(encoding="utf-8")

        return {
            "text": text,
            "source": path.name,
        }

    def load_directory(self, directory: str) -> list[dict]:
        path = Path(directory)

        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        documents = []

        for file_path in sorted(path.glob("*.md")):
            documents.append(self.load(str(file_path)))

        return documents