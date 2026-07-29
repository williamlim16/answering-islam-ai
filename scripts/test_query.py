#!/usr/bin/env python3
"""CLI script to test querying ChromaDB."""
import sys
import argparse
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import EMBEDDING_MODEL

def main():
    parser = argparse.ArgumentParser(description="Test querying ChromaDB.")
    parser.add_argument("query", help="The query string to search for")
    parser.add_argument("--host", default="auth-proxy-production-1868.up.railway.app", help="ChromaDB Host")
    parser.add_argument("--port", type=int, default=443, help="ChromaDB Port")
    parser.add_argument("--api-key", default="b79d8q6m8k9sr9jz", help="API Key for ChromaDB")
    parser.add_argument("--collection", default="answering_islam", help="Collection name")
    parser.add_argument("--top-k", type=int, default=3, help="Number of results to retrieve")
    args = parser.parse_args()

    print(f"Connecting to ChromaDB at {args.host}:{args.port}...")
    
    client = chromadb.HttpClient(
        host=args.host,
        port=args.port,
        ssl=True,
        headers={"Authorization": f"Bearer {args.api_key}", "X-Chroma-Token": args.api_key}
    )
    
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)

    try:
        collection = client.get_collection(
            name=args.collection,
            embedding_function=emb_fn
        )
    except Exception as e:
        print(f"Error getting collection: {e}")
        sys.exit(1)
        
    print(f"\nSearching for: '{args.query}'\n")
    
    results = collection.query(
        query_texts=[args.query],
        n_results=args.top_k
    )
    
    if not results['documents'] or not results['documents'][0]:
        print("No results found.")
        return
        
    for i in range(len(results['documents'][0])):
        doc = results['documents'][0][i]
        meta = results['metadatas'][0][i]
        dist = results['distances'][0][i]
        
        print(f"--- Result {i+1} (Distance/Score: {dist:.4f}) ---")
        print(f"Title : {meta.get('article_title', 'Unknown')}")
        print(f"Author: {meta.get('author', 'Unknown')}")
        print(f"Topic : {meta.get('topic', 'Unknown')}")
        print(f"URL   : {meta.get('article_url', 'Unknown')}")
        print(f"\nContent Snippet:\n{doc[:400]}...\n")

if __name__ == "__main__":
    main()
