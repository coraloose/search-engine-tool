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


# Results should be ranked by descending TF-IDF score.
def test_find_ranks_results_by_tfidf_for_basic_query() -> None:
    search_engine = build_search_engine()

    results = search_engine.find(["truth"])

    assert results[0]["doc_id"] == "2"
    assert results[0]["score"] == "1.6927"


# If scores are tied, lower document ids should come first.
def test_find_breaks_score_ties_by_document_id() -> None:
    search_engine = build_search_engine()

    results = search_engine.find(["life"])

    assert results[0]["doc_id"] == "1"
    assert results[1]["doc_id"] == "3"
    assert results[0]["score"] == "1.1249"
    assert results[1]["score"] == "1.1249"


# AND-based search should fail if any query word is missing.
def test_find_returns_empty_list_when_one_query_term_is_missing() -> None:
    search_engine = build_search_engine()

    results = search_engine.find(["good", "missing"])

    assert results == []


# TF-IDF should rank documents using weighted term importance.
def test_find_ranks_results_by_tfidf_score() -> None:
    documents = {
        1: {"url": "https://example.com/page1"},
        2: {"url": "https://example.com/page2"},
        3: {"url": "https://example.com/page3"},
        4: {"url": "https://example.com/page4"},
        5: {"url": "https://example.com/page5"},
        6: {"url": "https://example.com/page6"},
        7: {"url": "https://example.com/page7"},
        8: {"url": "https://example.com/page8"},
        9: {"url": "https://example.com/page9"},
        10: {"url": "https://example.com/page10"},
        11: {"url": "https://example.com/page11"},
        12: {"url": "https://example.com/page12"},
    }

    index = {
        "common": {
            "doc_freq": 12,
            "postings": {
                1: {"frequency": 4, "positions": [0, 1, 2, 3]},
                2: {"frequency": 1, "positions": [0]},
                3: {"frequency": 2, "positions": [0, 1]},
                4: {"frequency": 2, "positions": [0, 1]},
                5: {"frequency": 2, "positions": [0, 1]},
                6: {"frequency": 2, "positions": [0, 1]},
                7: {"frequency": 2, "positions": [0, 1]},
                8: {"frequency": 2, "positions": [0, 1]},
                9: {"frequency": 2, "positions": [0, 1]},
                10: {"frequency": 2, "positions": [0, 1]},
                11: {"frequency": 2, "positions": [0, 1]},
                12: {"frequency": 2, "positions": [0, 1]},
            },
        },
        "rare": {
            "doc_freq": 2,
            "postings": {
                1: {"frequency": 1, "positions": [4]},
                2: {"frequency": 3, "positions": [1, 2, 3]},
            },
        },
    }

    search_engine = SearchEngine(index, documents)
    results = search_engine.find(["common", "rare"])

    assert results[0]["doc_id"] == "2"
    assert results[1]["doc_id"] == "1"


# Exact phrase queries should only return documents containing adjacent words.
def test_find_supports_exact_phrase_queries() -> None:
    documents = {
        1: {"url": "https://example.com/page1"},
        2: {"url": "https://example.com/page2"},
    }

    index = {
        "good": {
            "doc_freq": 2,
            "postings": {
                1: {"frequency": 1, "positions": [0]},
                2: {"frequency": 1, "positions": [0]},
            },
        },
        "friends": {
            "doc_freq": 2,
            "postings": {
                1: {"frequency": 1, "positions": [1]},
                2: {"frequency": 1, "positions": [2]},
            },
        },
        "make": {
            "doc_freq": 1,
            "postings": {
                2: {"frequency": 1, "positions": [1]},
            },
        },
    }

    search_engine = SearchEngine(index, documents)
    results = search_engine.find(["good friends"])

    assert len(results) == 1
    assert results[0]["doc_id"] == "1"


# Phrase search should reject documents where the words appear in the wrong order.
def test_find_phrase_search_rejects_wrong_word_order() -> None:
    documents = {
        1: {"url": "https://example.com/page1"},
    }

    index = {
        "good": {
            "doc_freq": 1,
            "postings": {
                1: {"frequency": 1, "positions": [1]},
            },
        },
        "friends": {
            "doc_freq": 1,
            "postings": {
                1: {"frequency": 1, "positions": [0]},
            },
        },
    }

    search_engine = SearchEngine(index, documents)
    results = search_engine.find(["good friends"])

    assert results == []


# Phrase matches should receive a ranking bonus.
def test_find_phrase_matches_receive_phrase_bonus() -> None:
    documents = {
        1: {"url": "https://example.com/page1"},
        2: {"url": "https://example.com/page2"},
    }

    index = {
        "good": {
            "doc_freq": 2,
            "postings": {
                1: {"frequency": 2, "positions": [0, 3]},
                2: {"frequency": 2, "positions": [0, 1]},
            },
        },
        "friends": {
            "doc_freq": 2,
            "postings": {
                1: {"frequency": 2, "positions": [2, 4]},
                2: {"frequency": 2, "positions": [1, 2]},
            },
        },
    }

    search_engine = SearchEngine(index, documents)
    results = search_engine.find(["good friends"])

    assert results[0]["doc_id"] == "2"


# Mixed keyword and phrase queries should require both conditions.
def test_find_supports_mixed_keyword_and_phrase_query() -> None:
    search_engine = build_search_engine()

    results = search_engine.find(["life", "good friends"])

    assert len(results) == 1
    assert results[0]["doc_id"] == "1"


# Blank or punctuation-only query parts should produce no matches.
def test_find_returns_empty_list_for_blank_or_punctuation_only_query_parts() -> None:
    search_engine = build_search_engine()

    results = search_engine.find(["   ", "!!!"])

    assert results == []