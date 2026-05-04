import json
import re
from pathlib import Path
from typing import Any, Dict, List


class Indexer:
    """
    Builds, stores, and loads an inverted index for crawled pages.

    The index is case-insensitive and stores, for each word:
    - document frequency
    - postings by document
    - term frequency within each document
    - word positions within each document

    The index structure is designed to support the coursework requirements
    for efficient word lookup and multi-word query processing.
    """

    def __init__(self) -> None:
        """
        Initialise the indexer with empty document and index collections.
        """
        self.index: Dict[str, Dict[str, Any]] = {}
        self.documents: Dict[int, Dict[str, str]] = {}

    def tokenize(self, text: str) -> List[str]:
        """
        Convert raw text into a normalised list of searchable tokens.

        The tokenisation strategy is intentionally simple and appropriate
        for this coursework:
        - convert all text to lowercase
        - extract alphabetic words and apostrophe-containing words
        - ignore punctuation and case differences

        Args:
            text: The raw input text.

        Returns:
            A list of normalised word tokens.
        """
        return re.findall(r"[a-zA-Z']+", text.lower())

    def add_document(self, doc_id: int, url: str, text: str) -> None:
        """
        Add a single document to the inverted index.

        This method tokenises the text and records:
        - the document URL
        - the frequency of each word in the document
        - the positions at which each word appears

        Args:
            doc_id: The internal numeric identifier of the document.
            url: The document URL.
            text: The extracted searchable text of the document.
        """
        self.documents[doc_id] = {"url": url}

        tokens = self.tokenize(text)

        for position, token in enumerate(tokens):
            if token not in self.index:
                self.index[token] = {
                    "doc_freq": 0,
                    "postings": {}
                }

            postings = self.index[token]["postings"]

            if doc_id not in postings:
                postings[doc_id] = {
                    "frequency": 0,
                    "positions": []
                }
                self.index[token]["doc_freq"] += 1

            postings[doc_id]["frequency"] += 1
            postings[doc_id]["positions"].append(position)

    def build_from_pages(self, pages: List[Dict[str, str]]) -> None:
        """
        Build the full inverted index from a list of crawled pages.

        Each page is expected to contain:
        - 'url': the page URL
        - 'text': the extracted searchable content

        Existing index data is cleared before rebuilding.

        Args:
            pages: A list of crawled page dictionaries.
        """
        self.index.clear()
        self.documents.clear()

        for doc_id, page in enumerate(pages, start=1):
            url = page.get("url", "")
            text = page.get("text", "")
            self.add_document(doc_id, url, text)

    def save(self, filepath: str) -> None:
        """
        Save the current index and document metadata to disk as JSON.

        The output is stored as a single file for simplicity, as permitted
        by the coursework specification.

        Args:
            filepath: The destination file path.
        """
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "documents": self.documents,
            "index": self.index,
            "metadata": {
                "total_documents": len(self.documents),
                "total_terms": len(self.index)
            }
        }

        with path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2)

    def load(self, filepath: str) -> None:
        """
        Load a previously saved index from disk.

        JSON object keys are read back as strings, so document identifiers
        in both the documents collection and postings lists are converted
        back to integers after loading.

        Args:
            filepath: The path to the saved index file.
        """
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
                "postings": converted_postings
            }