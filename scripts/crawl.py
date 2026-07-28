#!/usr/bin/env python3
"""CLI script to crawl answering-islam.org."""
import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.crawler.scraper import Crawler
from config import BASE_URL, CRAWL_DELAY, MAX_PAGES


def main():
    parser = argparse.ArgumentParser(description="Crawl answering-islam.org")
    parser.add_argument("--base-url", default=BASE_URL, help="Base URL to crawl")
    parser.add_argument("--delay", type=float, default=CRAWL_DELAY, help="Delay between requests per worker (seconds)")
    parser.add_argument("--max-pages", type=int, default=MAX_PAGES, help="Maximum pages to crawl")
    parser.add_argument("--concurrency", type=int, default=5, help="Number of concurrent workers (default: 5)")
    parser.add_argument("--start", help="Starting URL (default: base_url/index.html)")
    args = parser.parse_args()

    # Override config if provided
    import config
    config.MAX_PAGES = args.max_pages

    crawler = Crawler(
        base_url=args.base_url,
        delay=args.delay,
        concurrency=args.concurrency,
    )
    manifest = crawler.crawl(start_url=args.start)

    print(f"\nCrawl complete: {len(manifest)} pages saved to data/raw/")


if __name__ == "__main__":
    main()
