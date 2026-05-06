# Search Engine Tool

## Project Overview

This project is a Python command-line search engine developed for the COMP3011 Web Services and Web Data coursework.

The application crawls the target website `https://quotes.toscrape.com/`, extracts searchable content from each page, builds an inverted index, stores the index in the file system, and allows users to search for words and multi-word queries through a command-line interface.

The system is designed to demonstrate the core stages of a simple search engine pipeline:

- web crawling
- text extraction
- inverted index construction
- index persistence
- query processing and retrieval

The search is case-insensitive and stores word statistics such as document frequency, term frequency, and word positions.

---

## Features

- Crawls all pages from `https://quotes.toscrape.com/`
- Respects a politeness window of at least 6 seconds between requests
- Extracts quote text, author names, and tags from each page
- Builds an inverted index with:
  - document frequency
  - term frequency
  - word positions
- Saves the index to a JSON file
- Loads the saved index from disk
- Supports single-word and multi-word search queries
- Supports printing the inverted index entry for a specific word
- Includes automated tests for crawler, indexer, search, and command handling

---

## Project Structure

```text
search-engine-tool/
├─ src/
│  ├─ __init__.py
│  ├─ crawler.py
│  ├─ indexer.py
│  ├─ search.py
│  └─ main.py
├─ tests/
│  ├─ __init__.py
│  ├─ test_crawler.py
│  ├─ test_indexer.py
│  ├─ test_search.py
│  └─ test_main.py
├─ data/
│  └─ index.json
├─ requirements.txt
├─ README.md
└─ .gitignore
```

---

## Dependencies

This project uses the following main dependencies:

- `requests` — for sending HTTP requests
- `beautifulsoup4` — for parsing HTML pages
- `pytest` — for automated testing
- `pytest-cov` — for test coverage measurement

Install all dependencies with:

```bash
pip install -r requirements.txt
```

---

## Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/coraloose/search-engine-tool.git
cd search-engine-tool
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

You can run the command-line tool from the `src` directory:

```bash
cd src
python main.py
```

---

## Command-Line Usage

When the program starts, it opens a simple shell interface.

### `build`

Crawls the target website, builds the inverted index, and saves it to disk.

```text
> build
```

### `load`

Loads a previously saved index from the file system.

```text
> load
```

### `print <word>`

Prints the inverted index entry for a specific word.

```text
> print truth
```

Example output:

```text
Inverted index for 'truth':
{'doc_freq': 5, 'postings': {2: {'frequency': 1, 'positions': [19]}, ...}}
```

### `find <word1> [word2] [word3] ...`

Finds all pages containing the given query word or words.

```text
> find life
> find good friends
```

Example output:

```text
Matching pages:
- doc_id=2 score=11 url=https://quotes.toscrape.com/page/2/
- doc_id=6 score=3 url=https://quotes.toscrape.com/page/6/
```

### `help`

Displays the list of supported commands.

```text
> help
```

### `exit`

Quits the program.

```text
> exit
```

---

## How the System Works

### Crawling

The crawler starts from the homepage of `https://quotes.toscrape.com/` and follows pagination links until no further pages are available.

It extracts:
- quote text
- author names
- tags

The crawler uses a politeness delay of at least 6 seconds between successive requests, in line with the coursework requirements.

### Indexing

The indexer tokenises extracted text into lowercase words and builds an inverted index.

For each word, the index stores:
- `doc_freq`: number of documents containing the word
- `postings`: document-level information, including:
  - `frequency`
  - `positions`

### Search

The search engine supports:
- single-word queries
- multi-word queries using an AND-based search model

For multi-word queries, only documents containing all query terms are returned.

Results are ranked using a simple relevance score based on the sum of term frequencies of the query words in each matching document.

---

## Testing

This project includes automated tests for all core components:

- crawler
- indexer
- search
- command handling in `main.py`

### Run all tests

```bash
pytest -v
```

### Run test coverage

```bash
pytest --cov=src --cov-report=term-missing
```

### Current test coverage

At the current stage of development, the project achieves approximately 80% overall coverage across the `src` package.

---

## Example Workflow

A typical usage session looks like this:

```text
> build
> print truth
> find life
> find good friends
> load
> exit
```

---

## Design Decisions

### Why an inverted index?

An inverted index allows efficient lookup of words and documents.  
Instead of scanning every page for every query, the system can directly retrieve the postings list for each query term.

### Why store positions?

Storing positions provides more detailed statistics about where words occur in a page. It also makes the design easier to extend in the future for phrase queries or proximity-based ranking.

### Why use JSON for persistence?

JSON is simple, readable, easy to debug, and suitable for storing the entire index in a single file, which matches the coursework brief.

### Why is search case-insensitive?

The coursework specifies that search should not be case-sensitive, so all tokens are normalised to lowercase during indexing and querying.

---

## Error Handling

The application includes basic error handling for:

- failed HTTP requests
- missing index files
- empty user commands
- invalid command usage
- empty or unmatched queries

---

## Future Improvements

Possible future improvements include:

- TF-IDF ranking instead of simple term-frequency scoring
- phrase search using word positions
- stop-word filtering
- stemming or lemmatisation
- exporting search results in a richer format

---

## Author

Created for COMP3011 Web Services and Web Data coursework.

---

## GenAI Usage Note

Generative AI tools were used during development as support tools for drafting code structure, refining tests, and reviewing design decisions.  
All generated suggestions were manually reviewed, tested, and adapted before inclusion in the final implementation.
