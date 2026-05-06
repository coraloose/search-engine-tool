from typing import Any, Optional


class SearchEngine:
    # Provide lookup and query functionality over an inverted index.
    def __init__(
        self,
        index: dict[str, Any],
        documents: dict[int, dict[str, str]],
    ) -> None:
        self.index = index
        self.documents = documents

    # Return the index entry for a single word.
    def print_word(self, word: str) -> Optional[dict[str, Any]]:
        return self.index.get(word.lower())

    # Return the set of document IDs containing the given word.
    def _get_posting_doc_ids(self, word: str) -> set[int]:
        entry = self.index.get(word)
        if not entry:
            return set()

        postings = entry.get("postings", {})
        return {int(doc_id) for doc_id in postings.keys()}

    # Calculate a simple term-frequency score for one document.
    def _calculate_score(self, doc_id: int, query_words: list[str]) -> int:
        score = 0

        for word in query_words:
            entry = self.index.get(word)
            if not entry:
                continue

            posting = entry.get("postings", {}).get(doc_id)
            if posting:
                score += posting.get("frequency", 0)

        return score

    # Return documents containing all query terms.
    def find(self, query_words: list[str]) -> list[dict[str, str]]:
        if not query_words:
            return []

        normalised_words = [word.lower() for word in query_words if word.strip()]
        if not normalised_words:
            return []

        doc_sets: list[set[int]] = []

        for word in normalised_words:
            doc_ids = self._get_posting_doc_ids(word)
            if not doc_ids:
                return []
            doc_sets.append(doc_ids)

        matching_doc_ids = set.intersection(*doc_sets) if doc_sets else set()

        ranked_results = []
        for doc_id in matching_doc_ids:
            document = self.documents.get(doc_id)
            if not document:
                continue

            ranked_results.append(
                {
                    "doc_id": str(doc_id),
                    "url": document["url"],
                    "score": str(self._calculate_score(doc_id, normalised_words)),
                }
            )

        # Sort by descending score, then ascending doc_id.
        ranked_results.sort(
            key=lambda result: (-int(result["score"]), int(result["doc_id"]))
        )

        return ranked_results