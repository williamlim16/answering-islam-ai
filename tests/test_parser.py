from src.crawler.parser import parse_article, extract_links

SAMPLE_HTML = """
<html>
<head><title>Test Article Title</title></head>
<body>
<div class="all">
  <div class="left"><!-- nav --></div>
  <div class="right">
    <div class="content">
      <div class="csc-default">
        <p>This is the article content about Christianity and Islam.</p>
        <p>It has multiple paragraphs with important arguments.</p>
      </div>
    </div>
  </div>
</div>
</body>
</html>
"""

def test_parse_article_extracts_title():
    article = parse_article(SAMPLE_HTML, "https://example.com/test.html")
    assert article.title == "Test Article Title"

def test_parse_article_extracts_content():
    article = parse_article(SAMPLE_HTML, "https://example.com/test.html")
    assert "article content" in article.content
    assert "multiple paragraphs" in article.content

def test_parse_article_no_nav():
    article = parse_article(SAMPLE_HTML, "https://example.com/test.html")
    assert "nav" not in article.content.lower() or len(article.content) > 50

def test_extract_links():
    html = '<a href="authors/green/article.html">Link</a><a href="https://external.com">External</a>'
    links = extract_links(html, "https://www.answering-islam.org")
    assert any("answering-islam" in l for l in links)

def test_extract_links_skips_external():
    html = '<a href="https://external.com/page">External</a>'
    links = extract_links(html, "https://www.answering-islam.org")
    assert len(links) == 0

def test_extract_links_skips_non_english():
    html = '''
    <a href="Arabic/article.html">Arabic</a>
    <a href="French/article.html">French</a>
    <a href="chinese/article.html">Chinese</a>
    <a href="authors/green/article.html">English</a>
    '''
    links = extract_links(html, "https://www.answering-islam.org")
    assert len(links) == 1
    assert "authors/green" in links[0]
