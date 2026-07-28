"""BFS web crawler for answering-islam.org with concurrent fetching."""
import asyncio
import json
import hashlib
from pathlib import Path
from collections import deque

import aiohttp
from tqdm import tqdm

from config import BASE_URL, CRAWL_DELAY, MAX_PAGES, REQUEST_TIMEOUT, RAW_DIR
from .parser import extract_links


class Crawler:
    """Concurrent BFS crawler that discovers and downloads all pages on the site."""

    def __init__(
        self,
        base_url: str = BASE_URL,
        delay: float = CRAWL_DELAY,
        concurrency: int = 5,
    ):
        self.base_url = base_url.rstrip("/")
        self.delay = delay
        self.concurrency = concurrency
        self.visited: set[str] = set()
        self.queue: deque[str] = deque()
        self.raw_dir = Path(RAW_DIR)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.manifest: list[dict] = []
        self._lock = asyncio.Lock()
        self._pbar: tqdm | None = None

    def _url_to_filename(self, url: str) -> str:
        """Convert URL to a safe filename."""
        url_hash = hashlib.md5(url.encode()).hexdigest()
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

    async def _fetch(self, session: aiohttp.ClientSession, url: str) -> str | None:
        """Fetch a URL with rate limiting and error handling."""
        try:
            await asyncio.sleep(self.delay)
            async with session.get(
                url, timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
            ) as response:
                response.raise_for_status()
                return await response.text()
        except Exception as e:
            print(f"  ✗ Error fetching {url}: {e}")
            return None

    async def _worker(
        self,
        session: aiohttp.ClientSession,
        semaphore: asyncio.Semaphore,
    ):
        """Worker that fetches URLs from the queue and discovers new links."""
        while True:
            try:
                url = self.queue.popleft()
            except IndexError:
                # Queue empty — wait a bit then check again
                await asyncio.sleep(0.1)
                if self.queue:
                    continue
                return

            if url in self.visited:
                continue

            if len(self.visited) >= MAX_PAGES:
                return

            async with semaphore:
                html = await self._fetch(session, url)

            if html is None:
                continue

            # Save raw HTML
            filename = self._url_to_filename(url)
            filepath = self.raw_dir / filename
            filepath.write_text(html, encoding="utf-8")

            # Record in manifest
            async with self._lock:
                self.manifest.append({
                    "url": url,
                    "filename": filename,
                    "size": len(html),
                })
                self.visited.add(url)
                if self._pbar:
                    self._pbar.update(1)

            # Discover new links
            new_links = extract_links(html, self.base_url)
            for link in new_links:
                if link not in self.visited and link not in self.queue:
                    self.queue.append(link)

            # Save manifest periodically
            if len(self.visited) % 10 == 0:
                async with self._lock:
                    self._save_manifest()

    async def _crawl(self, start_url: str | None = None) -> list[dict]:
        """Run async BFS crawl from the start URL."""
        self._load_manifest()

        start = start_url or self.base_url + "/index.html"
        if start not in self.visited:
            self.queue.append(start)

        semaphore = asyncio.Semaphore(self.concurrency)
        self._pbar = tqdm(total=len(self.visited), desc="Crawling", unit="pages")

        headers = {
            "User-Agent": "AnsweringIslamRAG/1.0 (Academic Research Crawler)"
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            workers = [
                asyncio.create_task(
                    self._worker(session, semaphore)
                )
                for _ in range(self.concurrency)
            ]
            await asyncio.gather(*workers)

        self._save_manifest()
        if self._pbar:
            self._pbar.close()
        print(f"\n✓ Crawled {len(self.visited)} pages")
        return self.manifest

    def crawl(self, start_url: str | None = None) -> list[dict]:
        """Run BFS crawl from the start URL (sync entry point)."""
        return asyncio.run(self._crawl(start_url))
