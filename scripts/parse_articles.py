#!/usr/bin/env python3
"""CLI script to parse raw HTML pages into clean Articles."""
import sys
import json
import argparse
from pathlib import Path

from tqdm import tqdm

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.crawler.parser import parse_article
from config import RAW_DIR

def main():
    parser = argparse.ArgumentParser(description="Parse raw HTML pages into clean Articles.")
    parser.add_argument("--output", default="data/articles.jsonl", help="Output JSONL file path (default: data/articles.jsonl)")
    args = parser.parse_args()

    raw_dir = Path(RAW_DIR)
    manifest_path = raw_dir / "manifest.json"
    
    if not manifest_path.exists():
        print(f"Error: Manifest not found at {manifest_path}")
        print("Please run scripts/crawl.py first.")
        sys.exit(1)
        
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
        
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Parsing {len(manifest)} articles...")
    
    success_count = 0
    error_count = 0
    
    with open(output_path, "w", encoding="utf-8") as out_f:
        for item in tqdm(manifest, desc="Parsing", unit="article"):
            filename = item["filename"]
            url = item["url"]
            filepath = raw_dir / filename
            
            if not filepath.exists():
                print(f"\nWarning: Missing file {filename} for URL {url}")
                error_count += 1
                continue
                
            try:
                html_content = filepath.read_text(encoding="utf-8", errors="replace")
                article = parse_article(html_content, url)
                
                out_f.write(article.model_dump_json() + "\n")
                success_count += 1
            except Exception as e:
                print(f"\nError parsing {filename}: {e}")
                error_count += 1
                
    print(f"\nParsing complete:")
    print(f"  ✓ Successfully parsed: {success_count}")
    if error_count > 0:
        print(f"  ✗ Failed to parse: {error_count}")
    print(f"Output saved to {output_path}")

if __name__ == "__main__":
    main()
