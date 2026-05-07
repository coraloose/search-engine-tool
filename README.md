# Search Engine Tool

## Project Overview

This project is a Python command-line search engine developed for the COMP3011 Web Services and Web Data coursework.

The application crawls the target website `https://quotes.toscrape.com/`, extracts searchable content from each page, builds an inverted index, saves the index to disk, and allows users to search for words, multi-word queries, and exact phrases through a command-line interface.

The system demonstrates the core stages of a simple search engine pipeline:

- web crawling
- text extraction
- inverted index construction
- index persistence
- ranked query processing and retrieval

The search is case-insensitive, and the index stores word statistics such as document frequency, term frequency, and word positions.

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
- Supports single-word and multi-word AND queries
- Supports exact phrase search using quotation marks
- Ranks results using TF-IDF scoring
- Applies a phrase-match bonus to exact phrase queries
- Prints the inverted index entry for a specific word
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

Run the command-line tool from the `src` directory:

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

Loads a previously saved index from disk.

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

### `find <words...> ["exact phrase"]`

Returns all pages containing all query terms, with results ranked by TF-IDF score.

```text
> find life
> find good friends
```

### `find "exact phrase"`

Finds only pages containing the exact quoted phrase.

```text
> find "good friends"
```

### `find <word> "exact phrase"`

Supports mixed keyword and phrase queries.

```text
> find life "good friends"
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

## Example Workflow

A typical usage session looks like this:

```text
> build
> print truth
> find good friends
> find "good friends"
> find life
> load
> exit
```

---

## Architecture Overview

The project is organised into four main modules:

### `crawler.py`

Responsible for:

- sending HTTP requests
- respecting the politeness delay
- extracting quote text, author names, and tags
- following pagination links across the target website

### `indexer.py`

Responsible for:

- normalising and tokenising text
- building the inverted index
- storing document metadata
- saving and loading index data as JSON

### `search.py`

Responsible for:

- retrieving postings for query terms
- processing single-word, multi-word, and phrase queries
- computing TF-IDF ranking scores
- checking positional adjacency for exact phrase matching

### `main.py`

Responsible for:

- the interactive command-line shell
- parsing user commands
- calling build, load, print, and find operations
- handling invalid input and command errors gracefully

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

The indexer tokenises extracted text into lowercase searchable words and builds an inverted index.

For each word, the index stores:

- `doc_freq`: number of documents containing the word
- `postings`: document-level information, including:
  - `frequency`
  - `positions`

The tokenizer also normalises accented characters and curly apostrophes so that tokens are stored more consistently.

### Search

The search engine supports:

- single-word queries
- multi-word AND queries
- exact phrase queries using quotation marks
- mixed keyword and phrase queries

Results are ranked using TF-IDF scoring rather than simple raw term frequency.

For exact phrase queries, the engine also checks whether the words occur in adjacent positions within the same document and applies a phrase-match bonus to improve ranking quality.

---

## Ranking Strategy

### Baseline idea

A simple ranking strategy would be to sort documents by raw term frequency. This is easy to implement, but it can overvalue very common words.

### Current approach: TF-IDF

This project uses TF-IDF-inspired ranking:

- **TF (term frequency)** measures how often a word appears in a document
- **IDF (inverse document frequency)** gives more weight to rarer terms
- the final score is the sum of weighted term contributions across the query

This makes ranking more meaningful because rare but important words contribute more strongly than very common words.

### Phrase bonus

For exact phrase queries, the engine applies an additional phrase-match bonus when the phrase appears contiguously in a document. This helps exact phrase matches rank above documents that merely contain the same individual terms.

---

## Design Decisions

### Why an inverted index?

An inverted index allows efficient lookup of words and documents. Instead of scanning every page for every query, the system can directly retrieve the postings list for each query term.

### Why store positions?

Storing positions makes it possible to:

- record richer term statistics
- support phrase matching
- extend the system more easily for future proximity-based features

### Why use JSON for persistence?

JSON is simple, readable, easy to debug, and suitable for storing the entire index in a single file, which matches the coursework brief.

### Why is search case-insensitive?

The coursework specifies that search should not be case-sensitive, so all tokens are normalised to lowercase during indexing and querying.

### Why add TF-IDF and phrase search?

These features extend the basic coursework requirements and make the search behaviour more realistic:

- TF-IDF improves ranking quality
- phrase search improves retrieval precision
- both features are directly supported by the positional inverted index design

---

## Testing Strategy

This project includes automated tests for all core components:

- crawler
- indexer
- search
- command handling in `main.py`

The test suite covers:

- successful and failed page fetching
- pagination handling
- tokenisation behaviour
- inverted index construction
- build/load persistence
- single-word and multi-word search
- TF-IDF ranking behaviour
- exact phrase matching
- command parsing and shell interaction
- edge cases such as empty input, invalid quotes, and missing query terms

### Run all tests

```bash
pytest -v
```

### Run test coverage

```bash
pytest --cov=src --cov-report=term-missing
```

### Current coverage

The current test suite achieves **92% total coverage** across the `src` package.

---

## Error Handling

The application includes error handling for:

- failed HTTP requests
- missing index files
- invalid command usage
- empty user commands
- invalid quotation syntax in the CLI
- unmatched or missing queries
- build and load failures in the command loop

---

## Performance Notes

This project is designed for correctness and clarity rather than large-scale optimisation, but the implementation still uses efficient structures for this coursework scenario.

- **Index building** is roughly proportional to the total number of tokens processed.
- **Keyword search** is based on postings-list intersection for AND-style matching.
- **Phrase search** is more expensive than keyword search because it also checks positional adjacency.
- **TF-IDF ranking** adds additional score computation per matching document, but remains efficient for the small course dataset.

For this coursework dataset, the performance is sufficient for interactive command-line use.

---

## Limitations and Future Improvements

Current limitations include:

- no stemming or lemmatisation
- no stop-word filtering
- no snippet generation in search results
- phrase search is exact and order-sensitive
- the index is stored in a single JSON file rather than a more scalable storage backend

Possible future improvements include:

- query suggestions or spelling correction
- Boolean query operators
- snippet previews for matched results
- stop-word removal and stemming
- proximity ranking beyond exact phrase matching
- alternative storage backends for larger datasets

---

## Author

Created for COMP3011 Web Services and Web Data coursework.

---

## GenAI Usage Note

Generative AI tools were used during development as support tools for drafting code structure, refining tests, reviewing design decisions, and improving documentation.

All generated suggestions were manually reviewed, tested, and adapted before inclusion in the final implementation.

The final submitted code, tests, and design choices were verified and understood manually rather than accepted uncritically.
