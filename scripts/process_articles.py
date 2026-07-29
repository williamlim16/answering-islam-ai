#!/usr/bin/env python3
"""Process raw HTML files into structured articles."""
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.crawler.parser import parse_article
from src.crawler.models import Article

def main():
    raw_dir = Path("data/raw")
    output_file = Path("data/articles.json")
    
    if not raw_dir.exists():
        print(f"Error: {raw_dir} does not exist")
        sys.exit(1)
    
    html_files = list(raw_dir.glob("*.html"))
    print(f"Found {len(html_files)} HTML files")
    
    articles = []
    errors = []
    
    for i, html_file in enumerate(html_files):
        try:
            # Read HTML with encoding fallback
            try:
                html = html_file.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                html = html_file.read_text(encoding="latin-1")
            
            # Parse article
            # Construct a fake URL from filename for topic inference
            url = f"https://www.answering-islam.org/{html_file.name}"
            article = parse_article(html, url)
            
            # Only keep articles with meaningful content
            if len(article.content) > 100:
                art_dict = article.model_dump()
                # Convert datetime to string for JSON serialization
                if "crawled_at" in art_dict:
                    art_dict["crawled_at"] = art_dict["crawled_at"].isoformat()
                articles.append(art_dict)
                
            if (i + 1) % 50 == 0:
                print(f"  Processed {i + 1}/{len(html_files)} files...")
                
        except Exception as e:
            errors.append({"file": html_file.name, "error": str(e)})
    
    # Save articles
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Processed {len(articles)} articles")
    print(f"✓ Saved to {output_file}")
    
    if errors:
        print(f"\n⚠ {len(errors)} errors:")
        for err in errors[:10]:
            print(f"  - {err['file']}: {err['error']}")
    
    # Print some stats
    topics = {}
    for art in articles:
        topic = art.get("topic", "Unknown")
        topics[topic] = topics.get(topic, 0) + 1
    
    print(f"\n📊 Topic distribution:")
    for topic, count in sorted(topics.items(), key=lambda x: -x[1])[:10]:
        print(f"  {topic}: {count}")

if __name__ == "__main__":
    main()
