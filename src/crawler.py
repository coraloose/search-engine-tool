import time
from dataclasses import dataclass
from typing import List, Optional, Set
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag


@dataclass
class CrawledPage:
    """
    Represents a single crawled webpage.

    Attributes:
        url: The absolute URL of the crawled page.
        text: The extracted searchable text content from the page.
    """
    url: str
    text: str


class Crawler:
    """
    Crawls pages from the target website and extracts searchable text.

    This crawler is designed specifically for the coursework target website:
    https://quotes.toscrape.com/

    Main responsibilities:
    1. Send HTTP requests to retrieve pages.
    2. Respect a politeness delay between successive requests.
    3. Extract quotes, authors, and tags from each page.
    4. Follow pagination links to continue crawling.
    5. Avoid revisiting pages that have already been crawled.
    """

    def __init__(self, base_url: str, delay: int = 6, timeout: int = 15) -> None:
        """
        Initialise the crawler.

        Args:
            base_url: The starting URL for crawling.
            delay: Minimum delay in seconds between consecutive requests.
            timeout: Timeout in seconds for HTTP requests.
        """
        self.base_url = base_url
        self.delay = delay
        self.timeout = timeout
        self.session = requests.Session()
        self.visited_urls: Set[str] = set()
        self.last_request_time: Optional[float] = None

        # A custom User-Agent is included to identify the client more clearly.
        self.session.headers.update(
            {
                "User-Agent": (
                    "COMP3011-SearchEngineTool/1.0 "
                    "(Coursework crawler for educational use)"
                )
            }
        )

    def _wait_if_needed(self) -> None:
        """
        Enforce the politeness window between HTTP requests.

        If a previous request was made less than `self.delay` seconds ago,
        the crawler waits for the remaining time before making the next request.
        """
        if self.last_request_time is None:
            return

        elapsed_time = time.time() - self.last_request_time
        remaining_delay = self.delay - elapsed_time

        if remaining_delay > 0:
            time.sleep(remaining_delay)

    def fetch_page(self, url: str) -> Optional[str]:
        """
        Retrieve the HTML content of a webpage.

        This method respects the configured politeness delay before sending
        a request. If the request fails for any reason, None is returned.

        Args:
            url: The absolute URL to request.

        Returns:
            The HTML content as a string if successful, otherwise None.
        """
        self._wait_if_needed()

        try:
            response = self.session.get(url, timeout=self.timeout)
            self.last_request_time = time.time()
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            print(f"Failed to fetch {url}: {exc}")
            return None

    def extract_page_text(self, html: str) -> str:
        """
        Extract searchable text from a page.

        For the target website, the most relevant searchable content includes:
        - quote text
        - author names
        - quote tags

        These fields are concatenated into a single plain-text string.

        Args:
            html: The raw HTML content of the page.

        Returns:
            A single string containing the extracted textual content.
        """
        soup = BeautifulSoup(html, "html.parser")
        text_parts: List[str] = []

        quote_blocks = soup.find_all("div", class_="quote")

        for quote_block in quote_blocks:
            if not isinstance(quote_block, Tag):
                continue

            quote_text_element = quote_block.find("span", class_="text")
            author_element = quote_block.find("small", class_="author")
            tag_elements = quote_block.find_all("a", class_="tag")

            if quote_text_element and quote_text_element.get_text(strip=True):
                text_parts.append(quote_text_element.get_text(strip=True))

            if author_element and author_element.get_text(strip=True):
                text_parts.append(author_element.get_text(strip=True))

            for tag_element in tag_elements:
                tag_text = tag_element.get_text(strip=True)
                if tag_text:
                    text_parts.append(tag_text)

        return " ".join(text_parts)

    def find_next_page_url(self, html: str, current_url: str) -> Optional[str]:
        """
        Identify the URL of the next page in the pagination sequence.

        Args:
            html: The raw HTML content of the current page.
            current_url: The absolute URL of the current page.

        Returns:
            The absolute URL of the next page if it exists, otherwise None.
        """
        soup = BeautifulSoup(html, "html.parser")

        next_li = soup.find("li", class_="next")
        if not next_li or not isinstance(next_li, Tag):
            return None

        next_link = next_li.find("a")
        if not next_link or not isinstance(next_link, Tag):
            return None

        href = next_link.get("href")
        if not href:
            return None

        return urljoin(current_url, href)

    def is_valid_url(self, url: str) -> bool:
        """
        Determine whether a URL should be crawled.

        Only URLs from the same domain as the base URL are considered valid.

        Args:
            url: The URL to validate.

        Returns:
            True if the URL is valid for crawling, otherwise False.
        """
        base_netloc = urlparse(self.base_url).netloc
        candidate_netloc = urlparse(url).netloc
        return candidate_netloc == base_netloc

    def crawl(self) -> List[dict]:
        """
        Crawl the target website starting from the base URL.

        The crawler follows pagination links until no further pages are found.
        Each successfully crawled page is returned as a dictionary containing
        its URL and extracted text.

        Returns:
            A list of dictionaries in the form:
            [
                {"url": "...", "text": "..."},
                ...
            ]
        """
        pages: List[dict] = []
        current_url: Optional[str] = self.base_url

        while current_url:
            if current_url in self.visited_urls:
                break

            if not self.is_valid_url(current_url):
                print(f"Skipping invalid URL outside target domain: {current_url}")
                break

            print(f"Crawling: {current_url}")
            self.visited_urls.add(current_url)

            html = self.fetch_page(current_url)
            if html is None:
                break

            page_text = self.extract_page_text(html)
            pages.append(
                {
                    "url": current_url,
                    "text": page_text,
                }
            )

            current_url = self.find_next_page_url(html, current_url)

        print(f"Crawling complete. Total pages crawled: {len(pages)}")
        return pages