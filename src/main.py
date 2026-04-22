from pathlib import Path

from crawler import Crawler
from indexer import Indexer
from search import SearchEngine


BASE_URL = "https://quotes.toscrape.com/"
INDEX_FILE = Path("data/index.json")


def print_help() -> None:
    print("\nAvailable commands:")
    print("  build               Crawl the site, build the index, and save it")
    print("  load                Load the index from disk")
    print("  print <word>        Print the inverted index entry for a word")
    print("  find <words...>     Find pages containing all query words")
    print("  help                Show this help message")
    print("  exit                Quit the program\n")


def main() -> None:
    indexer = Indexer()
    search_engine = None

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

        elif command == "exit":
            print("Goodbye.")
            break

        elif command == "build":
            print("Building index...")
            crawler = Crawler(BASE_URL, delay=6)
            pages = crawler.crawl()

            indexer.build_from_pages(pages)
            indexer.save(str(INDEX_FILE))

            search_engine = SearchEngine(indexer.index, indexer.documents)
            print(f"Index built and saved to {INDEX_FILE}")

        elif command == "load":
            if not INDEX_FILE.exists():
                print(f"Index file not found: {INDEX_FILE}")
                continue

            indexer.load(str(INDEX_FILE))
            search_engine = SearchEngine(indexer.index, indexer.documents)
            print(f"Index loaded from {INDEX_FILE}")

        elif command == "print":
            if not search_engine:
                print("Please run 'build' or 'load' first.")
                continue

            if len(args) != 1:
                print("Usage: print <word>")
                continue

            word = args[0]
            result = search_engine.print_word(word)

            if result is None:
                print(f"No index entry found for '{word}'.")
            else:
                print(f"Inverted index for '{word}':")
                print(result)

        elif command == "find":
            if not search_engine:
                print("Please run 'build' or 'load' first.")
                continue

            if not args:
                print("Usage: find <word1> [word2] [word3] ...")
                continue

            results = search_engine.find(args)

            if not results:
                print("No matching pages found.")
            else:
                print("Matching pages:")
                for result in results:
                    print(f"- doc_id={result['doc_id']} url={result['url']}")

        else:
            print(f"Unknown command: {command}")
            print("Type 'help' to see available commands.")


if __name__ == "__main__":
    main()