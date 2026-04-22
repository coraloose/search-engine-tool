from typing import Dict, Any, List, Set


class SearchEngine:
    def __init__(self, index: Dict[str, Any], documents: Dict[int, Dict[str, str]]) -> None:
        self.index = index
        self.documents = documents

    def print_word(self, word: str) -> Dict[str, Any] | None:
        return self.index.get(word.lower())

    def find(self, query_words: List[str]) -> List[Dict[str, str]]:
        if not query_words:
            return []

        normalized_words = [word.lower() for word in query_words]

        doc_sets: List[Set[int]] = []
        for word in normalized_words:
            entry = self.index.get(word)
            if not entry:
                return []

            postings = entry.get("postings", {})
            doc_ids = {int(doc_id) for doc_id in postings.keys()}
            doc_sets.append(doc_ids)

        matching_doc_ids = set.intersection(*doc_sets) if doc_sets else set()

        results = []
        for doc_id in sorted(matching_doc_ids):
            doc = self.documents.get(doc_id) or self.documents.get(str(doc_id))
            if doc:
                results.append({
                    "doc_id": str(doc_id),
                    "url": doc["url"]
                })

        return results