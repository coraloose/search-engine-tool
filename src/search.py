from typing import Any, Dict, List, Optional, Set


class SearchEngine:
    """
    Provides lookup and query functionality over an inverted index.

    This class supports:
    - retrieving the index entry for a single word
    - processing single-word and multi-word queries
    - returning documents that contain all query terms

    Query processing is case-insensitive and uses an AND-based model
    for multi-word search, meaning that a result document must contain
    every query term.
    """

    def __init__(self, index: Dict[str, Any], documents: Dict[int, Dict[str, str]]) -> None:
        """
        Initialise the search engine.

        Args:
            index: The inverted index structure.
            documents: Document metadata indexed by document identifier.
        """
        self.index = index
        self.documents = documents

    def print_word(self, word: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve the inverted index entry for a single word.

        Args:
            word: The search word.

        Returns:
            The index entry if the word exists, otherwise None.
        """
        normalised_word = word.lower()
        return self.index.get(normalised_word)

    def _get_posting_doc_ids(self, word: str) -> Set[int]:
        """
        Retrieve the set of document identifiers containing a given word.

        Args:
            word: A normalised query word.

        Returns:
            A set of document identifiers containing the word.
            If the word does not exist in the index, an empty set is returned.
        """
        entry = self.index.get(word)
        if not entry:
            return set()

        postings = entry.get("postings", {})
        return {int(doc_id) for doc_id in postings.keys()}

    def _calculate_score(self, doc_id: int, query_words: List[str]) -> int:
        """
        Calculate a simple relevance score for a document.

        The current implementation uses the sum of term frequencies of all
        query words within the document. This provides a straightforward
        ranking strategy for coursework purposes.

        Args:
            doc_id: The document identifier.
            query_words: A list of normalised query terms.

        Returns:
            An integer relevance score.
        """
        score = 0

        for word in query_words:
            entry = self.index.get(word)
            if not entry:
                continue

            posting = entry.get("postings", {}).get(doc_id)
            if posting:
                score += posting.get("frequency", 0)

        return score

    def find(self, query_words: List[str]) -> List[Dict[str, str]]:
        """
        Find documents containing all query words.

        The query is processed in a case-insensitive manner. For multi-word
        queries, only documents containing every query term are returned.

        Results are ranked by a simple relevance score based on the total
        term frequency of the query words within each document. Ties are
        broken by document identifier.

        Args:
            query_words: A list of raw query terms.

        Returns:
            A list of matching documents, where each result contains:
            - doc_id
            - url
            - score
        """
        if not query_words:
            return []

        normalised_words = [word.lower() for word in query_words if word.strip()]
        if not normalised_words:
            return []

        doc_sets: List[Set[int]] = []

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

        ranked_results.sort(
            key=lambda result: (-int(result["score"]), int(result["doc_id"]))
        )

        return ranked_results