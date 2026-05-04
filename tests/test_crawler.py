from unittest.mock import Mock, patch

import requests

from src.crawler import Crawler

# Sample HTML containing a quote, author, tags, and a next-page link.
SAMPLE_HTML = """
<html>
  <body>
    <div class="quote">
      <span class="text">"A witty saying proves nothing."</span>
      <span>
        <small class="author">Voltaire</small>
      </span>
      <div class="tags">
        <a class="tag">wisdom</a>
        <a class="tag">humor</a>
      </div>
    </div>
    <li class="next">
      <a href="/page/2/">Next</a>
    </li>
  </body>
</html>
"""

# Sample HTML without pagination.
LAST_PAGE_HTML = """
<html>
  <body>
    <div class="quote">
      <span class="text">"Life is what happens to us while we are making other plans."</span>
      <span>
        <small class="author">Allen Saunders</small>
      </span>
      <div class="tags">
        <a class="tag">life</a>
      </div>
    </div>
  </body>
</html>
"""


# The crawler should accept URLs from the target domain.
def test_is_valid_url_accepts_same_domain() -> None:
    crawler = Crawler("https://quotes.toscrape.com/")

    assert crawler.is_valid_url("https://quotes.toscrape.com/page/2/")


# The crawler should reject URLs outside the target domain.
def test_is_valid_url_rejects_different_domain() -> None:
    crawler = Crawler("https://quotes.toscrape.com/")

    assert not crawler.is_valid_url("https://example.com/page/2/")


# Text extraction should include quote text, author, and tags.
def test_extract_page_text_collects_searchable_content() -> None:
    crawler = Crawler("https://quotes.toscrape.com/")

    extracted_text = crawler.extract_page_text(SAMPLE_HTML)

    assert "A witty saying proves nothing." in extracted_text
    assert "Voltaire" in extracted_text
    assert "wisdom" in extracted_text
    assert "humor" in extracted_text


# The crawler should find the correct next-page URL.
def test_find_next_page_url_returns_absolute_url() -> None:
    crawler = Crawler("https://quotes.toscrape.com/")

    next_url = crawler.find_next_page_url(
        SAMPLE_HTML,
        "https://quotes.toscrape.com/"
    )

    assert next_url == "https://quotes.toscrape.com/page/2/"


# The crawler should return None when no next-page link exists.
def test_find_next_page_url_returns_none_when_no_next_link_exists() -> None:
    crawler = Crawler("https://quotes.toscrape.com/")

    next_url = crawler.find_next_page_url(
        LAST_PAGE_HTML,
        "https://quotes.toscrape.com/page/10/"
    )

    assert next_url is None


# Successful page fetches should return HTML content.
@patch("src.crawler.requests.Session.get")
def test_fetch_page_returns_html_on_success(mock_get: Mock) -> None:
    crawler = Crawler("https://quotes.toscrape.com/", delay=0)

    mock_response = Mock()
    mock_response.text = SAMPLE_HTML
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    html = crawler.fetch_page("https://quotes.toscrape.com/")

    assert html == SAMPLE_HTML
    mock_get.assert_called_once()


# Failed page fetches should return None.
@patch("src.crawler.requests.Session.get")
def test_fetch_page_returns_none_on_request_failure(mock_get: Mock) -> None:
    crawler = Crawler("https://quotes.toscrape.com/", delay=0)

    mock_get.side_effect = requests.RequestException("Network failure")

    html = crawler.fetch_page("https://quotes.toscrape.com/")

    assert html is None


# Crawling should follow pagination and return all discovered pages.
@patch.object(Crawler, "fetch_page")
def test_crawl_follows_next_page_links(mock_fetch_page: Mock) -> None:
    crawler = Crawler("https://quotes.toscrape.com/", delay=0)

    mock_fetch_page.side_effect = [SAMPLE_HTML, LAST_PAGE_HTML]

    pages = crawler.crawl()

    assert len(pages) == 2
    assert pages[0]["url"] == "https://quotes.toscrape.com/"
    assert pages[1]["url"] == "https://quotes.toscrape.com/page/2/"
    assert "Voltaire" in pages[0]["text"]
    assert "Allen Saunders" in pages[1]["text"]


# Crawling should stop if page retrieval fails.
@patch.object(Crawler, "fetch_page")
def test_crawl_stops_when_fetch_fails(mock_fetch_page: Mock) -> None:
    crawler = Crawler("https://quotes.toscrape.com/", delay=0)

    mock_fetch_page.return_value = None

    pages = crawler.crawl()

    assert pages == []