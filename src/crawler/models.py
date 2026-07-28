"""Data models for the crawler and indexer."""
from datetime import datetime
from pydantic import BaseModel, Field


class Article(BaseModel):
    """A single crawled article from answering-islam.org."""
    url: str
    title: str
    author: str = "Unknown"
    topic: str = "Uncategorized"
    content: str  # clean text/markdown
    html: str  # raw HTML for reference
    crawled_at: datetime = Field(default_factory=datetime.now)
    word_count: int = 0

    def model_post_init(self, __context) -> None:
        if self.word_count == 0:
            self.word_count = len(self.content.split())


class Chunk(BaseModel):
    """A chunk of an article for embedding and retrieval."""
    article_url: str
    article_title: str
    author: str
    topic: str
    chunk_index: int
    content: str  # the chunk text
    metadata: dict = Field(default_factory=dict)

    def model_post_init(self, __context) -> None:
        self.metadata.update({
            "article_url": self.article_url,
            "article_title": self.article_title,
            "author": self.author,
            "topic": self.topic,
            "chunk_index": self.chunk_index,
        })
