"""BFS web crawler for answering-islam.org."""
import time
import json
import hashlib
from pathlib import Path
from collections import deque

import requests
from tqdm import tqdm

from config import BASE_URL, CRAWL_DELAY, MAX_PAGES, REQUEST_TIMEOUT, RAW_DIR
from .parser import extract_links


class Crawler:
    """BFS crawler that discovers and downloads all pages on the site."""

    def __init__(self, base_url: str = BASE_URL, delay: float = CRAWL_DELAY):
        self.base_url = base_url.rstrip("/")
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "AnsweringIslamRAG/1.0 (Academic Research Crawler)"
        })
        self.visited: set[str] = set()
        self.queue: deque[str] = deque()
        self.raw_dir = Path(RAW_DIR)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.manifest: list[dict] = []

    def _url_to_filename(self, url: str) -> str:
        """Convert URL to a safe filename."""
        # Create a hash-based filename to avoid path issues
        url_hash = hashlib.md5(url.encode()).hexdigest()
        # Also keep a readable suffix
        suffix = url.split("/")[-1][:30].replace(".", "_")
        return f"{suffix}_{url_hash}.html"

    def _load_manifest(self) -> None:
        """Load existing manifest to resume crawling."""
        manifest_path = self.raw_dir / "manifest.json"
        if manifest_path.exists():
            with open(manifest_path) as f:
                self.manifest = json.load(f)
            self.visited = {item["url"] for item in self.manifest}
            print(f"Resuming: {len(self.visited)} pages already crawled")

    def _save_manifest(self) -> None:
        """Save the crawl manifest."""
        manifest_path = self.raw_dir / "manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(self.manifest, f, indent=2)

    def fetch(self, url: str) -> str | None:
        """Fetch a URL with rate limiting and error handling."""
        try:
            time.sleep(self.delay)
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"  ✗ Error fetching {url}: {e}")
            return None

    def crawl(self, start_url: str | None = None) -> list[dict]:
        """Run BFS crawl from the start URL."""
        self._load_manifest()

        start = start_url or self.base_url + "/index.html"
        if start not in self.visited:
            self.queue.append(start)

        pbar = tqdm(total=len(self.visited), desc="Crawling", unit="pages")

        while self.queue and len(self.visited) < MAX_PAGES:
            url = self.queue.popleft()

            if url in self.visited:
                continue

            print(f"  → {url}")
            html = self.fetch(url)
            if html is None:
                continue

            # Save raw HTML
            filename = self._url_to_filename(url)
            filepath = self.raw_dir / filename
            filepath.write_text(html, encoding="utf-8")

            # Record in manifest
            self.manifest.append({
                "url": url,
                "filename": filename,
                "size": len(html),
            })
            self.visited.add(url)
            pbar.update(1)

            # Discover new links
            new_links = extract_links(html, self.base_url)
            for link in new_links:
                if link not in self.visited:
                    self.queue.append(link)

            # Save manifest periodically
            if len(self.visited) % 10 == 0:
                self._save_manifest()

        self._save_manifest()
        pbar.close()
        print(f"\n✓ Crawled {len(self.visited)} pages")
        return self.manifest
