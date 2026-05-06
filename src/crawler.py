import time
from typing import Optional, Set
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag


class Crawler:
    # Crawl the target website and extract searchable page text.
    def __init__(self, base_url: str, delay: int = 6, timeout: int = 15) -> None:
        self.base_url = base_url
        self.delay = delay
        self.timeout = timeout
        self.session = requests.Session()
        self.visited_urls: Set[str] = set()
        self.last_request_time: Optional[float] = None

        # Identify the crawler more clearly in outgoing requests.
        self.session.headers.update(
            {
                "User-Agent": (
                    "COMP3011-SearchEngineTool/1.0 "
                    "(Coursework crawler for educational use)"
                )
            }
        )

    # Respect the politeness delay between requests.
    def _wait_if_needed(self) -> None:
        if self.last_request_time is None:
            return

        elapsed = time.time() - self.last_request_time
        remaining = self.delay - elapsed

        if remaining > 0:
            time.sleep(remaining)

    # Fetch one page and return its HTML content.
    def fetch_page(self, url: str) -> Optional[str]:
        self._wait_if_needed()

        try:
            response = self.session.get(url, timeout=self.timeout)
            self.last_request_time = time.time()
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            print(f"Failed to fetch {url}: {exc}")
            return None

    # Extract quote text, author names, and tags from a page.
    def extract_page_text(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        text_parts: list[str] = []

        quote_blocks = soup.find_all("div", class_="quote")

        for quote_block in quote_blocks:
            if not isinstance(quote_block, Tag):
                continue

            quote_text = quote_block.find("span", class_="text")
            author = quote_block.find("small", class_="author")
            tags = quote_block.find_all("a", class_="tag")

            if quote_text and quote_text.get_text(strip=True):
                text_parts.append(quote_text.get_text(strip=True))

            if author and author.get_text(strip=True):
                text_parts.append(author.get_text(strip=True))

            for tag in tags:
                tag_text = tag.get_text(strip=True)
                if tag_text:
                    text_parts.append(tag_text)

        return " ".join(text_parts)

    # Return the next-page URL if pagination continues.
    def find_next_page_url(self, html: str, current_url: str) -> Optional[str]:
        soup = BeautifulSoup(html, "html.parser")

        next_item = soup.find("li", class_="next")
        if not next_item or not isinstance(next_item, Tag):
            return None

        next_link = next_item.find("a")
        if not next_link or not isinstance(next_link, Tag):
            return None

        href = next_link.get("href")
        if not href:
            return None

        return urljoin(current_url, href)

    # Check whether a URL belongs to the target domain.
    def is_valid_url(self, url: str) -> bool:
        base_netloc = urlparse(self.base_url).netloc
        candidate_netloc = urlparse(url).netloc
        return candidate_netloc == base_netloc

    # Crawl all reachable pages starting from the base URL.
    def crawl(self) -> list[dict[str, str]]:
        pages: list[dict[str, str]] = []
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
            pages.append({"url": current_url, "text": page_text})

            current_url = self.find_next_page_url(html, current_url)

        print(f"Crawling complete. Total pages crawled: {len(pages)}")
        return pages