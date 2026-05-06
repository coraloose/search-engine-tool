from pathlib import Path
from unittest.mock import Mock, patch

from src import main


# print_help should show the supported commands.
def test_print_help_displays_available_commands(capsys) -> None:
    main.print_help()

    captured = capsys.readouterr()

    assert "Available commands:" in captured.out
    assert "build" in captured.out
    assert "load" in captured.out
    assert "print <word>" in captured.out
    assert 'find <words...> ["phrase"]' in captured.out
    assert "exit" in captured.out


# build_index should crawl pages, build the index, and save it.
@patch("src.main.SearchEngine")
@patch("src.main.Crawler")
def test_build_index_builds_and_saves_index(
    mock_crawler_class: Mock,
    mock_search_engine_class: Mock,
    capsys,
) -> None:
    indexer = Mock()
    indexer.documents = {
        1: {"url": "https://example.com/page1"},
    }
    indexer.index = {
        "good": {"doc_freq": 1, "postings": {}},
    }

    mock_crawler = Mock()
    mock_crawler.crawl.return_value = [
        {"url": "https://example.com/page1", "text": "good friends"},
    ]
    mock_crawler_class.return_value = mock_crawler

    mock_search_engine = Mock()
    mock_search_engine_class.return_value = mock_search_engine

    result = main.build_index(indexer)

    captured = capsys.readouterr()

    assert "Building index..." in captured.out
    assert "Index built and saved to" in captured.out
    assert "Total documents indexed: 1" in captured.out
    assert "Total unique terms indexed: 1" in captured.out

    mock_crawler_class.assert_called_once_with(main.BASE_URL, delay=6)
    mock_crawler.crawl.assert_called_once()
    indexer.build_from_pages.assert_called_once_with(
        [{"url": "https://example.com/page1", "text": "good friends"}]
    )
    indexer.save.assert_called_once_with(str(main.INDEX_FILE))
    mock_search_engine_class.assert_called_once_with(
        indexer.index,
        indexer.documents,
    )
    assert result == mock_search_engine


# load_index should return None when the index file does not exist.
@patch("src.main.INDEX_FILE", new=Path("nonexistent_index.json"))
def test_load_index_returns_none_when_index_file_is_missing(capsys) -> None:
    indexer = Mock()

    result = main.load_index(indexer)

    captured = capsys.readouterr()

    assert result is None
    assert "Index file not found" in captured.out
    assert "Please run 'build' first." in captured.out


# load_index should load the index and return a SearchEngine instance.
@patch("src.main.SearchEngine")
@patch("src.main.INDEX_FILE", new=Path(__file__))
def test_load_index_loads_existing_index(
    mock_search_engine_class: Mock,
    capsys,
) -> None:
    indexer = Mock()
    indexer.documents = {
        1: {"url": "https://example.com/page1"},
    }
    indexer.index = {
        "truth": {"doc_freq": 1, "postings": {}},
    }

    mock_search_engine = Mock()
    mock_search_engine_class.return_value = mock_search_engine

    result = main.load_index(indexer)

    captured = capsys.readouterr()

    indexer.load.assert_called_once_with(str(main.INDEX_FILE))
    mock_search_engine_class.assert_called_once_with(
        indexer.index,
        indexer.documents,
    )
    assert "Index loaded from" in captured.out
    assert "Total documents indexed: 1" in captured.out
    assert "Total unique terms indexed: 1" in captured.out
    assert result == mock_search_engine


# handle_print_command should warn if no search engine is available.
def test_handle_print_command_requires_loaded_search_engine(capsys) -> None:
    main.handle_print_command(None, ["truth"])

    captured = capsys.readouterr()

    assert "Please run 'build' or 'load' first." in captured.out


# handle_print_command should show usage when the argument count is invalid.
def test_handle_print_command_validates_argument_count(capsys) -> None:
    search_engine = Mock()

    main.handle_print_command(search_engine, [])
    captured = capsys.readouterr()
    assert "Usage: print <word>" in captured.out

    main.handle_print_command(search_engine, ["truth", "life"])
    captured = capsys.readouterr()
    assert "Usage: print <word>" in captured.out


# handle_print_command should report missing words.
def test_handle_print_command_reports_missing_word(capsys) -> None:
    search_engine = Mock()
    search_engine.print_word.return_value = None

    main.handle_print_command(search_engine, ["missing"])

    captured = capsys.readouterr()

    search_engine.print_word.assert_called_once_with("missing")
    assert "No index entry found for 'missing'." in captured.out


# handle_print_command should print the matching index entry.
def test_handle_print_command_displays_index_entry(capsys) -> None:
    search_engine = Mock()
    search_engine.print_word.return_value = {
        "doc_freq": 1,
        "postings": {1: {"frequency": 2, "positions": [0, 3]}},
    }

    main.handle_print_command(search_engine, ["Truth"])

    captured = capsys.readouterr()

    assert "Inverted index for 'truth':" in captured.out
    assert "doc_freq" in captured.out
    assert "positions" in captured.out


# handle_find_command should warn if no search engine is available.
def test_handle_find_command_requires_loaded_search_engine(capsys) -> None:
    main.handle_find_command(None, ["truth"])

    captured = capsys.readouterr()

    assert "Please run 'build' or 'load' first." in captured.out


# handle_find_command should show usage when no query terms are given.
def test_handle_find_command_validates_query_arguments(capsys) -> None:
    search_engine = Mock()

    main.handle_find_command(search_engine, [])

    captured = capsys.readouterr()

    assert 'Usage: find <word1> [word2] ["exact phrase"] ...' in captured.out


# handle_find_command should report when no pages match.
def test_handle_find_command_reports_no_matches(capsys) -> None:
    search_engine = Mock()
    search_engine.find.return_value = []

    main.handle_find_command(search_engine, ["missing"])

    captured = capsys.readouterr()

    search_engine.find.assert_called_once_with(["missing"])
    assert "No matching pages found." in captured.out


# handle_find_command should display ranked results.
def test_handle_find_command_displays_matching_pages(capsys) -> None:
    search_engine = Mock()
    search_engine.find.return_value = [
        {
            "doc_id": "2",
            "score": "5.0000",
            "url": "https://example.com/page2",
        },
        {
            "doc_id": "1",
            "score": "3.0000",
            "url": "https://example.com/page1",
        },
    ]

    main.handle_find_command(search_engine, ["good", "friends"])

    captured = capsys.readouterr()

    assert "Matching pages:" in captured.out
    assert "doc_id=2 score=5.0000 url=https://example.com/page2" in captured.out
    assert "doc_id=1 score=3.0000 url=https://example.com/page1" in captured.out


# handle_find_command should pass phrase-style arguments through unchanged.
def test_handle_find_command_passes_phrase_arguments_to_search_engine(capsys) -> None:
    search_engine = Mock()
    search_engine.find.return_value = [
        {
            "doc_id": "1",
            "score": "4.2500",
            "url": "https://example.com/page1",
        }
    ]

    main.handle_find_command(search_engine, ["good friends"])

    captured = capsys.readouterr()

    search_engine.find.assert_called_once_with(["good friends"])
    assert "doc_id=1 score=4.2500 url=https://example.com/page1" in captured.out