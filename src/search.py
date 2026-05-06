import math
import re
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

    # Tokenise a query component into searchable terms.
    def _tokenize_query_text(self, text: str) -> list[str]:
        text = text.lower()
        text = text.replace("’", "'").replace("‘", "'")
        return re.findall(r"[a-z]+(?:'[a-z]+)*", text)

    # Return the set of document IDs containing the given word.
    def _get_posting_doc_ids(self, word: str) -> set[int]:
        entry = self.index.get(word)
        if not entry:
            return set()

        postings = entry.get("postings", {})
        return {int(doc_id) for doc_id in postings.keys()}

    # Return the positions list for one word in one document.
    def _get_positions(self, word: str, doc_id: int) -> list[int]:
        entry = self.index.get(word)
        if not entry:
            return []

        posting = entry.get("postings", {}).get(doc_id)
        if not posting:
            return []

        return posting.get("positions", [])

    # Count how many times an exact phrase appears in a document.
    def _phrase_frequency(self, doc_id: int, phrase_tokens: list[str]) -> int:
        if not phrase_tokens:
            return 0

        if len(phrase_tokens) == 1:
            positions = self._get_positions(phrase_tokens[0], doc_id)
            return len(positions)

        position_sets = [set(self._get_positions(token, doc_id)) for token in phrase_tokens]

        if any(not positions for positions in position_sets):
            return 0

        phrase_count = 0
        for start_position in position_sets[0]:
            if all((start_position + offset) in position_sets[offset] for offset in range(1, len(phrase_tokens))):
                phrase_count += 1

        return phrase_count

    # Return the set of document IDs containing an exact phrase.
    def _get_phrase_doc_ids(self, phrase_tokens: list[str]) -> set[int]:
        if not phrase_tokens:
            return set()

        doc_sets = [self._get_posting_doc_ids(token) for token in phrase_tokens]
        if any(not doc_ids for doc_ids in doc_sets):
            return set()

        candidate_doc_ids = set.intersection(*doc_sets)
        return {
            doc_id
            for doc_id in candidate_doc_ids
            if self._phrase_frequency(doc_id, phrase_tokens) > 0
        }

    # Compute a smoothed inverse document frequency.
    def _idf(self, word: str) -> float:
        entry = self.index.get(word)
        if not entry:
            return 0.0

        total_documents = len(self.documents)
        document_frequency = entry.get("doc_freq", 0)

        if total_documents == 0 or document_frequency == 0:
            return 0.0

        return math.log10((total_documents + 1) / (document_frequency + 1)) + 1.0

    # Compute a log-scaled term frequency weight.
    def _tf_weight(self, word: str, doc_id: int) -> float:
        entry = self.index.get(word)
        if not entry:
            return 0.0

        posting = entry.get("postings", {}).get(doc_id)
        if not posting:
            return 0.0

        frequency = posting.get("frequency", 0)
        if frequency <= 0:
            return 0.0

        return 1.0 + math.log10(frequency)

    # Compute the final TF-IDF + phrase bonus score.
    def _calculate_score(
        self,
        doc_id: int,
        keyword_terms: list[str],
        phrase_terms: list[list[str]],
    ) -> float:
        score = 0.0

        # Standard TF-IDF contribution from individual terms.
        all_terms = keyword_terms + [token for phrase in phrase_terms for token in phrase]
        for word in all_terms:
            score += self._tf_weight(word, doc_id) * self._idf(word)

        # Extra bonus for exact phrase matches.
        for phrase_tokens in phrase_terms:
            phrase_frequency = self._phrase_frequency(doc_id, phrase_tokens)
            if phrase_frequency == 0:
                continue

            average_phrase_idf = sum(self._idf(token) for token in phrase_tokens) / len(phrase_tokens)
            phrase_bonus = phrase_frequency * len(phrase_tokens) * average_phrase_idf
            score += phrase_bonus

        return score

    # Find documents matching keywords and exact phrases.
    def find(self, query_parts: list[str]) -> list[dict[str, str]]:
        if not query_parts:
            return []

        keyword_terms: list[str] = []
        phrase_terms: list[list[str]] = []

        for query_part in query_parts:
            cleaned_part = query_part.strip()
            if not cleaned_part:
                continue

            tokens = self._tokenize_query_text(cleaned_part)
            if not tokens:
                continue

            # If a single CLI argument contains spaces, treat it as an exact phrase.
            if " " in cleaned_part and len(tokens) > 1:
                phrase_terms.append(tokens)
            else:
                keyword_terms.extend(tokens)

        if not keyword_terms and not phrase_terms:
            return []

        doc_sets: list[set[int]] = []

        for word in keyword_terms:
            doc_ids = self._get_posting_doc_ids(word)
            if not doc_ids:
                return []
            doc_sets.append(doc_ids)

        for phrase_tokens in phrase_terms:
            doc_ids = self._get_phrase_doc_ids(phrase_tokens)
            if not doc_ids:
                return []
            doc_sets.append(doc_ids)

        matching_doc_ids = set.intersection(*doc_sets) if doc_sets else set()

        ranked_results = []
        for doc_id in matching_doc_ids:
            document = self.documents.get(doc_id)
            if not document:
                continue

            score = self._calculate_score(doc_id, keyword_terms, phrase_terms)

            ranked_results.append(
                {
                    "doc_id": str(doc_id),
                    "url": document["url"],
                    "score": f"{score:.4f}",
                }
            )

        # Sort by descending score, then ascending doc_id.
        ranked_results.sort(
            key=lambda result: (-float(result["score"]), int(result["doc_id"]))
        )

        return ranked_results