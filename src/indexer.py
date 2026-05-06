import json
import re
from pathlib import Path
from typing import Any


class Indexer:
    # Build, save, and load an inverted index.
    def __init__(self) -> None:
        self.index: dict[str, dict[str, Any]] = {}
        self.documents: dict[int, dict[str, str]] = {}

    # Convert raw text into lowercase searchable tokens.
    def tokenize(self, text: str) -> list[str]:
        return re.findall(r"[a-zA-Z']+", text.lower())

    # Add one document and its tokens to the inverted index.
    def add_document(self, doc_id: int, url: str, text: str) -> None:
        self.documents[doc_id] = {"url": url}
        tokens = self.tokenize(text)

        for position, token in enumerate(tokens):
            if token not in self.index:
                self.index[token] = {"doc_freq": 0, "postings": {}}

            postings = self.index[token]["postings"]

            if doc_id not in postings:
                postings[doc_id] = {"frequency": 0, "positions": []}
                self.index[token]["doc_freq"] += 1

            postings[doc_id]["frequency"] += 1
            postings[doc_id]["positions"].append(position)

    # Build a fresh inverted index from crawled pages.
    def build_from_pages(self, pages: list[dict[str, str]]) -> None:
        self.index.clear()
        self.documents.clear()

        for doc_id, page in enumerate(pages, start=1):
            url = page.get("url", "")
            text = page.get("text", "")
            self.add_document(doc_id, url, text)

    # Save the current index to a JSON file.
    def save(self, filepath: str) -> None:
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "documents": self.documents,
            "index": self.index,
            "metadata": {
                "total_documents": len(self.documents),
                "total_terms": len(self.index),
            },
        }

        with path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2)

    # Load a saved index from a JSON file.
    def load(self, filepath: str) -> None:
        path = Path(filepath)

        with path.open("r", encoding="utf-8") as file:
            payload = json.load(file)

        raw_documents = payload.get("documents", {})
        raw_index = payload.get("index", {})

        self.documents = {
            int(doc_id): doc_info
            for doc_id, doc_info in raw_documents.items()
        }

        self.index = {}
        for word, entry in raw_index.items():
            raw_postings = entry.get("postings", {})
            converted_postings = {
                int(doc_id): posting
                for doc_id, posting in raw_postings.items()
            }

            self.index[word] = {
                "doc_freq": entry.get("doc_freq", 0),
                "postings": converted_postings,
            }