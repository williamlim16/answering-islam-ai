import re
from typing import List
from src.crawler.models import Article, Chunk

def chunk_text(text: str, max_words: int = 300, overlap_words: int = 50) -> List[str]:
    """Split text into overlapping chunks based on words."""
    words = text.split()
    if not words:
        return []
        
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + max_words])
        chunks.append(chunk)
        # Advance index, but stop if we are at the end
        if i + max_words >= len(words):
            break
        i += max_words - overlap_words
        
    return chunks

def chunk_article(article: Article, max_words: int = 300, overlap_words: int = 50) -> List[Chunk]:
    """Convert an Article into a list of Chunk models."""
    text_chunks = chunk_text(article.content, max_words, overlap_words)
    
    chunk_models = []
    for i, text_chunk in enumerate(text_chunks):
        chunk = Chunk(
            article_url=article.url,
            article_title=article.title,
            author=article.author,
            topic=article.topic,
            chunk_index=i,
            content=text_chunk,
        )
        chunk_models.append(chunk)
        
    return chunk_models
