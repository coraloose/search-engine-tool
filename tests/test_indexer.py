from pathlib import Path

from src.indexer import Indexer


# The tokenizer should normalise case and remove punctuation.
def test_tokenize_converts_text_to_lowercase_words() -> None:
    indexer = Indexer()

    tokens = indexer.tokenize("Hello, World! It's a GOOD day.")

    assert tokens == ["hello", "world", "it's", "a", "good", "day"]


# Adding a document should store its URL in the document collection.
def test_add_document_stores_document_metadata() -> None:
    indexer = Indexer()

    indexer.add_document(1, "https://example.com/page1", "simple text")

    assert 1 in indexer.documents
    assert indexer.documents[1]["url"] == "https://example.com/page1"


# Adding a document should create postings with correct frequency and positions.
def test_add_document_creates_index_entries_with_frequency_and_positions() -> None:
    indexer = Indexer()

    indexer.add_document(1, "https://example.com/page1", "good friends good")

    assert "good" in indexer.index
    assert indexer.index["good"]["doc_freq"] == 1
    assert indexer.index["good"]["postings"][1]["frequency"] == 2
    assert indexer.index["good"]["postings"][1]["positions"] == [0, 2]

    assert "friends" in indexer.index
    assert indexer.index["friends"]["doc_freq"] == 1
    assert indexer.index["friends"]["postings"][1]["frequency"] == 1
    assert indexer.index["friends"]["postings"][1]["positions"] == [1]


# Document frequency should count how many distinct documents contain a word.
def test_add_document_updates_document_frequency_across_multiple_documents() -> None:
    indexer = Indexer()

    indexer.add_document(1, "https://example.com/page1", "truth and love")
    indexer.add_document(2, "https://example.com/page2", "truth and hope")

    assert indexer.index["truth"]["doc_freq"] == 2
    assert 1 in indexer.index["truth"]["postings"]
    assert 2 in indexer.index["truth"]["postings"]


# Building from pages should index all supplied page data.
def test_build_from_pages_indexes_multiple_pages() -> None:
    indexer = Indexer()

    pages = [
        {"url": "https://example.com/page1", "text": "good friends"},
        {"url": "https://example.com/page2", "text": "good life"},
    ]

    indexer.build_from_pages(pages)

    assert len(indexer.documents) == 2
    assert indexer.index["good"]["doc_freq"] == 2
    assert indexer.index["friends"]["doc_freq"] == 1
    assert indexer.index["life"]["doc_freq"] == 1


# Rebuilding the index should clear any previous state first.
def test_build_from_pages_resets_previous_index_state() -> None:
    indexer = Indexer()

    first_pages = [
        {"url": "https://example.com/page1", "text": "old data"},
    ]
    second_pages = [
        {"url": "https://example.com/page2", "text": "new data"},
    ]

    indexer.build_from_pages(first_pages)
    assert "old" in indexer.index

    indexer.build_from_pages(second_pages)

    assert "old" not in indexer.index
    assert "new" in indexer.index
    assert len(indexer.documents) == 1
    assert indexer.documents[1]["url"] == "https://example.com/page2"


# Saving and loading should preserve document and index information.
def test_save_and_load_preserve_index_data(tmp_path: Path) -> None:
    indexer = Indexer()

    pages = [
        {"url": "https://example.com/page1", "text": "good friends good"},
        {"url": "https://example.com/page2", "text": "truth matters"},
    ]
    indexer.build_from_pages(pages)

    output_file = tmp_path / "index.json"
    indexer.save(str(output_file))

    loaded_indexer = Indexer()
    loaded_indexer.load(str(output_file))

    assert loaded_indexer.documents == indexer.documents
    assert loaded_indexer.index == indexer.index


# Saving should create the output file on disk.
def test_save_creates_output_file(tmp_path: Path) -> None:
    indexer = Indexer()
    indexer.build_from_pages(
        [{"url": "https://example.com/page1", "text": "sample text"}]
    )

    output_file = tmp_path / "nested" / "index.json"
    indexer.save(str(output_file))

    assert output_file.exists()


# Tokenising empty text should return an empty token list.
def test_tokenize_returns_empty_list_for_empty_text() -> None:
    indexer = Indexer()

    tokens = indexer.tokenize("")

    assert tokens == []


# Tokenisation should normalise accents and curly apostrophes.
def test_tokenize_handles_accents_and_curly_apostrophes() -> None:
    indexer = Indexer()

    tokens = indexer.tokenize("André said you’re doing fine.")

    assert tokens == ["andre", "said", "you're", "doing", "fine"]


# Tokenisation should keep valid unusual words rather than over-correcting them.
def test_tokenize_keeps_valid_words_after_normalisation() -> None:
    indexer = Indexer()

    tokens = indexer.tokenize(
        "Today you are You, that is truer than true. There is no one alive who is Youer than You."
    )

    assert "youer" in tokens
    assert "truer" in tokens
    assert "you" in tokens