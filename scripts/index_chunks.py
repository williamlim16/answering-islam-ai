#!/usr/bin/env python3
"""CLI script to embed chunks and index them into ChromaDB."""
import sys
import json
import argparse
from pathlib import Path
from tqdm import tqdm

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import hashlib

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.crawler.models import Chunk
from config import EMBEDDING_MODEL

def main():
    parser = argparse.ArgumentParser(description="Index chunks into ChromaDB.")
    parser.add_argument("--input", default="data/chunks.jsonl", help="Input JSONL file (default: data/chunks.jsonl)")
    parser.add_argument("--host", default="auth-proxy-production-1868.up.railway.app", help="ChromaDB Host")
    parser.add_argument("--port", type=int, default=443, help="ChromaDB Port (default: 443)")
    parser.add_argument("--api-key", default="b79d8q6m8k9sr9jz", help="API Key for ChromaDB")
    parser.add_argument("--collection", default="answering_islam", help="Collection name")
    parser.add_argument("--batch-size", type=int, default=100, help="Batch size for insertion")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found at {input_path}")
        sys.exit(1)

    print(f"Connecting to ChromaDB at {args.host}:{args.port}...")
    
    # Initialize Chroma client
    client = chromadb.HttpClient(
        host=args.host,
        port=args.port,
        ssl=True,
        headers={"Authorization": f"Bearer {args.api_key}", "X-Chroma-Token": args.api_key}
    )
    
    print(f"Loading embedding model: {EMBEDDING_MODEL} (this may take a moment to download on first run)")
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)

    print(f"Getting or creating collection '{args.collection}'...")
    collection = client.get_or_create_collection(
        name=args.collection,
        embedding_function=emb_fn,
        metadata={"hnsw:space": "cosine"}
    )
    
    print("Counting total chunks...")
    with open(input_path, "r", encoding="utf-8") as f:
        total_lines = sum(1 for _ in f)

    print(f"Indexing {total_lines} chunks into ChromaDB in batches of {args.batch_size}...")
    
    batch_ids = []
    batch_docs = []
    batch_metadatas = []

    success_count = 0

    with open(input_path, "r", encoding="utf-8") as f:
        for line in tqdm(f, total=total_lines, desc="Indexing", unit="chunk"):
            chunk_dict = json.loads(line)
            chunk = Chunk(**chunk_dict)
            
            # Create a unique ID for the chunk
            uid_str = f"{chunk.article_url}_{chunk.chunk_index}"
            chunk_id = hashlib.md5(uid_str.encode()).hexdigest()
            
            batch_ids.append(chunk_id)
            batch_docs.append(chunk.content)
            batch_metadatas.append(chunk.metadata)
            
            if len(batch_ids) >= args.batch_size:
                try:
                    collection.upsert(
                        ids=batch_ids,
                        documents=batch_docs,
                        metadatas=batch_metadatas
                    )
                    success_count += len(batch_ids)
                except Exception as e:
                    print(f"\nError indexing batch: {e}")
                
                # Clear batch
                batch_ids = []
                batch_docs = []
                batch_metadatas = []
                
        # Insert remainder
        if batch_ids:
            try:
                collection.upsert(
                    ids=batch_ids,
                    documents=batch_docs,
                    metadatas=batch_metadatas
                )
                success_count += len(batch_ids)
            except Exception as e:
                print(f"\nError indexing final batch: {e}")

    print(f"\nIndexing complete! Successfully upserted {success_count} chunks to collection '{args.collection}'.")
    
if __name__ == "__main__":
    main()
