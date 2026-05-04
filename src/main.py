from pathlib import Path

try:
    # Package-style imports for pytest and module execution.
    from .crawler import Crawler
    from .indexer import Indexer
    from .search import SearchEngine
except ImportError:
    # Fallback imports for direct script execution: python main.py
    from crawler import Crawler
    from indexer import Indexer
    from search import SearchEngine

BASE_URL = "https://quotes.toscrape.com/"

# Resolve paths relative to the project root rather than the current
# working directory, so the program behaves consistently no matter
# where it is launched from.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
INDEX_FILE = DATA_DIR / "index.json"


def print_help() -> None:
    """
    Display the list of supported shell commands.
    """
    print("\nAvailable commands:")
    print("  build               Crawl the site, build the index, and save it")
    print("  load                Load the index from disk")
    print("  print <word>        Print the inverted index entry for a word")
    print("  find <words...>     Find pages containing all query words")
    print("  help                Show this help message")
    print("  exit                Quit the program\n")


def build_index(indexer: Indexer) -> SearchEngine:
    """
    Crawl the target website, build the inverted index, and save it to disk.

    Args:
        indexer: The indexer instance used to construct and persist the index.

    Returns:
        A SearchEngine instance initialised with the newly built index.
    """
    print("Building index...")
    crawler = Crawler(BASE_URL, delay=6)
    pages = crawler.crawl()

    indexer.build_from_pages(pages)
    indexer.save(str(INDEX_FILE))

    print(f"Index built and saved to {INDEX_FILE}")
    print(f"Total documents indexed: {len(indexer.documents)}")
    print(f"Total unique terms indexed: {len(indexer.index)}")

    return SearchEngine(indexer.index, indexer.documents)


def load_index(indexer: Indexer) -> SearchEngine | None:
    """
    Load a previously saved index from disk.

    Args:
        indexer: The indexer instance used to load the stored index.

    Returns:
        A SearchEngine instance if loading succeeds, otherwise None.
    """
    if not INDEX_FILE.exists():
        print(f"Index file not found: {INDEX_FILE}")
        print("Please run 'build' first.")
        return None

    indexer.load(str(INDEX_FILE))
    print(f"Index loaded from {INDEX_FILE}")
    print(f"Total documents indexed: {len(indexer.documents)}")
    print(f"Total unique terms indexed: {len(indexer.index)}")

    return SearchEngine(indexer.index, indexer.documents)


def handle_print_command(search_engine: SearchEngine | None, args: list[str]) -> None:
    """
    Process the 'print' command.

    Args:
        search_engine: The active search engine instance, or None if the
            index has not yet been built or loaded.
        args: Command arguments supplied by the user.
    """
    if search_engine is None:
        print("Please run 'build' or 'load' first.")
        return

    if len(args) != 1:
        print("Usage: print <word>")
        return

    word = args[0]
    result = search_engine.print_word(word)

    if result is None:
        print(f"No index entry found for '{word}'.")
        return

    print(f"Inverted index for '{word.lower()}':")
    print(result)


def handle_find_command(search_engine: SearchEngine | None, args: list[str]) -> None:
    """
    Process the 'find' command.

    Args:
        search_engine: The active search engine instance, or None if the
            index has not yet been built or loaded.
        args: Command arguments supplied by the user.
    """
    if search_engine is None:
        print("Please run 'build' or 'load' first.")
        return

    if not args:
        print("Usage: find <word1> [word2] [word3] ...")
        return

    results = search_engine.find(args)

    if not results:
        print("No matching pages found.")
        return

    print("Matching pages:")
    for result in results:
        print(
            f"- doc_id={result['doc_id']} "
            f"score={result['score']} "
            f"url={result['url']}"
        )


def main() -> None:
    """
    Run the command-line shell for the search engine tool.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    indexer = Indexer()
    search_engine: SearchEngine | None = None

    print("Search Engine Tool")
    print("Type 'help' to see available commands.")

    while True:
        try:
            raw_command = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not raw_command:
            print("Please enter a command.")
            continue

        parts = raw_command.split()
        command = parts[0].lower()
        args = parts[1:]

        if command == "help":
            print_help()

        elif command == "build":
            try:
                search_engine = build_index(indexer)
            except Exception as exc:
                print(f"An error occurred while building the index: {exc}")

        elif command == "load":
            try:
                loaded_engine = load_index(indexer)
                if loaded_engine is not None:
                    search_engine = loaded_engine
            except Exception as exc:
                print(f"An error occurred while loading the index: {exc}")

        elif command == "print":
            handle_print_command(search_engine, args)

        elif command == "find":
            handle_find_command(search_engine, args)

        elif command == "exit":
            print("Goodbye.")
            break

        else:
            print(f"Unknown command: {command}")
            print("Type 'help' to see available commands.")


if __name__ == "__main__":
    main()