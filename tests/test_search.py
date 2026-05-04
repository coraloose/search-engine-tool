from src.indexer import Indexer
from src.search import SearchEngine


# Build a small reusable search engine for testing.
def build_search_engine() -> SearchEngine:
    indexer = Indexer()
    pages = [
        {"url": "https://example.com/page1", "text": "good friends good life"},
        {"url": "https://example.com/page2", "text": "good truth friends truth"},
        {"url": "https://example.com/page3", "text": "life hope wisdom"},
    ]
    indexer.build_from_pages(pages)
    return SearchEngine(indexer.index, indexer.documents)


# Existing words should return an index entry.
def test_print_word_returns_index_entry_for_existing_word() -> None:
    search_engine = build_search_engine()

    result = search_engine.print_word("good")

    assert result is not None
    assert result["doc_freq"] == 2


# Word lookup should be case-insensitive.
def test_print_word_is_case_insensitive() -> None:
    search_engine = build_search_engine()

    lower_result = search_engine.print_word("good")
    upper_result = search_engine.print_word("GOOD")

    assert lower_result == upper_result


# Missing words should return None.
def test_print_word_returns_none_for_missing_word() -> None:
    search_engine = build_search_engine()

    result = search_engine.print_word("missing")

    assert result is None


# Empty queries should return no results.
def test_find_returns_empty_list_for_empty_query() -> None:
    search_engine = build_search_engine()

    results = search_engine.find([])

    assert results == []


# Queries with absent words should return no results.
def test_find_returns_empty_list_for_non_existent_word() -> None:
    search_engine = build_search_engine()

    results = search_engine.find(["nonexistent"])

    assert results == []


# Single-word queries should return all matching documents.
def test_find_returns_single_word_matches() -> None:
    search_engine = build_search_engine()

    results = search_engine.find(["life"])

    returned_doc_ids = [result["doc_id"] for result in results]

    assert returned_doc_ids == ["1", "3"]


# Multi-word queries should return the intersection of matches.
def test_find_returns_intersection_for_multi_word_query() -> None:
    search_engine = build_search_engine()

    results = search_engine.find(["good", "friends"])

    returned_doc_ids = [result["doc_id"] for result in results]

    assert returned_doc_ids == ["1", "2"]


# Query matching should ignore case differences.
def test_find_is_case_insensitive() -> None:
    search_engine = build_search_engine()

    lower_results = search_engine.find(["truth"])
    mixed_results = search_engine.find(["TrUtH"])

    assert lower_results == mixed_results


# Results should be ranked by descending term-frequency score.
def test_find_ranks_results_by_term_frequency_score() -> None:
    search_engine = build_search_engine()

    results = search_engine.find(["truth"])

    assert results[0]["doc_id"] == "2"
    assert results[0]["score"] == "2"


# If scores are tied, lower document ids should come first.
def test_find_breaks_score_ties_by_document_id() -> None:
    search_engine = build_search_engine()

    results = search_engine.find(["life"])

    assert results[0]["doc_id"] == "1"
    assert results[1]["doc_id"] == "3"
    assert results[0]["score"] == "1"
    assert results[1]["score"] == "1"


# AND-based search should fail if any query word is missing.
def test_find_returns_empty_list_when_one_query_term_is_missing() -> None:
    search_engine = build_search_engine()

    results = search_engine.find(["good", "missing"])

    assert results == []