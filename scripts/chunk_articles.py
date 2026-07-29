#!/usr/bin/env python3
"""CLI script to chunk parsed Articles into Chunks."""
import sys
import json
import argparse
from pathlib import Path

from tqdm import tqdm

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.crawler.models import Article
from src.index.chunker import chunk_article

def main():
    parser = argparse.ArgumentParser(description="Chunk parsed Articles into Chunks.")
    parser.add_argument("--input", default="data/articles.jsonl", help="Input JSONL file (default: data/articles.jsonl)")
    parser.add_argument("--output", default="data/chunks.jsonl", help="Output JSONL file (default: data/chunks.jsonl)")
    parser.add_argument("--max-words", type=int, default=300, help="Maximum words per chunk")
    parser.add_argument("--overlap-words", type=int, default=50, help="Word overlap between chunks")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        print(f"Error: Input file not found at {input_path}")
        sys.exit(1)
        
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Reading articles from {input_path}...")
    
    total_articles = 0
    total_chunks = 0
    
    with open(input_path, "r", encoding="utf-8") as in_f:
        lines = in_f.readlines()
        
    with open(output_path, "w", encoding="utf-8") as out_f:
        for line in tqdm(lines, desc="Chunking", unit="article"):
            try:
                article_dict = json.loads(line)
                article = Article(**article_dict)
                
                chunks = chunk_article(article, args.max_words, args.overlap_words)
                
                for chunk in chunks:
                    out_f.write(chunk.model_dump_json() + "\n")
                    
                total_articles += 1
                total_chunks += len(chunks)
            except Exception as e:
                print(f"Error processing article: {e}")
                
    print(f"\nChunking complete:")
    print(f"  ✓ Processed articles: {total_articles}")
    print(f"  ✓ Generated chunks: {total_chunks}")
    print(f"Output saved to {output_path}")

if __name__ == "__main__":
    main()
