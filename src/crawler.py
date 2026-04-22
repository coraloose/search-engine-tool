from typing import List, Dict


class Crawler:
    def __init__(self, base_url: str, delay: int = 6) -> None:
        self.base_url = base_url
        self.delay = delay

    def crawl(self) -> List[Dict[str, str]]:
        """
        Temporary placeholder.
        Later this should crawl the target website and return a list of pages.
        Each page can be represented as:
        {"url": "...", "text": "..."}
        """
        return [
            {
                "url": self.base_url,
                "text": "Example quote text about good friends and indifference."
            }
        ]