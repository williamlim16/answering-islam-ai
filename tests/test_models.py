from src.crawler.models import Article, Chunk

def test_article_creation():
    article = Article(
        url="https://www.answering-islam.org/authors/green/crusade.html",
        title="The Islamic Support for the First Crusade",
        author="Samuel Green",
        topic="Responses",
        content="This is the full article text.",
        html="<div>...</div>",
    )
    assert article.url.startswith("https://")
    assert article.title
    assert article.author
    assert article.word_count == 6

def test_chunk_creation():
    chunk = Chunk(
        article_url="https://example.com/article.html",
        article_title="Test Article",
        author="Test Author",
        topic="Test Topic",
        chunk_index=0,
        content="This is a chunk of text...",
    )
    assert chunk.chunk_index == 0
    assert len(chunk.content) > 0
    assert chunk.metadata["article_url"] == "https://example.com/article.html"
    assert chunk.metadata["article_title"] == "Test Article"
    assert chunk.metadata["author"] == "Test Author"
    assert chunk.metadata["topic"] == "Test Topic"
    assert chunk.metadata["chunk_index"] == 0
