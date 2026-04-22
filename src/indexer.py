import json
from pathlib import Path
from typing import Dict, List, Any


class Indexer:
    def __init__(self) -> None:
        self.index: Dict[str, Dict[str, Any]] = {}
        self.documents: Dict[int, Dict[str, str]] = {}

    def build_from_pages(self, pages: List[Dict[str, str]]) -> None:
        """
        Temporary placeholder index builder.
        Later this should tokenize page text and build a real inverted index.
        """
        self.index = {
            "good": {
                "doc_freq": 1,
                "postings": {
                    1: {"frequency": 1, "positions": [5]}
                }
            },
            "friends": {
                "doc_freq": 1,
                "postings": {
                    1: {"frequency": 1, "positions": [6]}
                }
            },
            "indifference": {
                "doc_freq": 1,
                "postings": {
                    1: {"frequency": 1, "positions": [8]}
                }
            }
        }

        self.documents = {
            1: {"url": pages[0]["url"]}
        }

    def save(self, filepath: str) -> None:
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "index": self.index,
            "documents": self.documents
        }

        with path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    def load(self, filepath: str) -> None:
        path = Path(filepath)

        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)

        self.index = payload.get("index", {})
        self.documents = payload.get("documents", {})