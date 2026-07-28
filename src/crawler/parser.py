"""Parse answering-islam.org HTML pages into clean Articles."""
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from langdetect import detect, LangDetectException

def is_english(html: str) -> bool:
    """Check if the HTML content is in English using langdetect."""
    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text(separator=" ", strip=True)
    if not text:
        return False
    try:
        return detect(text) == 'en'
    except LangDetectException:
        return False

from .models import Article
from config import EXCLUDED_PATHS

# Topic mapping: URL path prefix → topic name
TOPIC_MAP = {
    "/Intro/": "Introductory Articles",
    "/God/": "Who Is God?",
    "/Who/": "Who Is Jesus?",
    "/Bible/": "The Bible",
    "/Basics/": "Basic Christianity",
    "/Testimonies/": "Why They Converted",
    "/Index/": "Index to Islam",
    "/Quran/": "The Qur'an",
    "/Muhammad/": "Muhammad",
    "/Responses/": "Polemics Rebuttals",
    "/Women/": "Women in Islam",
    "/NonMuslims/": "Under Islamic Rule",
    "/Terrorism/": "Islam & Terrorism",
    "/Emails/": "Email Dialogs",
    "/Q-A-panel/": "Questions & Answers",
    "/Authors/": "Authors",
    "/authors/": "Authors",
    "/Books/": "Books",
}


def infer_topic(url: str) -> str:
    """Infer the topic from the URL path."""
    for prefix, topic in TOPIC_MAP.items():
        if prefix in url:
            return topic
    return "Uncategorized"


def infer_author(html: str, url: str) -> str:
    """Try to extract the author from the page or URL."""
    # Try to find author in common patterns
    soup = BeautifulSoup(html, "lxml")

    # Check for author meta tags
    meta = soup.find("meta", attrs={"name": "author"})
    if meta and meta.get("content"):
        return meta["content"].strip()

    # Check for byline patterns
    for pattern in [
        r"(?:written|by|author)[:\s]+([A-Z][a-z]+ [A-Z][a-z]+)",
        r"©\s*\d{4}\s+([A-Z][a-z]+ [A-Z][a-z]+)",
    ]:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    # Fall back to URL path (e.g., /authors/green/ → green)
    url_lower = url.lower()
    for prefix in ["/authors/"]:
        if prefix in url_lower:
            parts = url_lower.split(prefix)
            if len(parts) > 1:
                author_slug = parts[1].split("/")[0].split(".")[0]
                return author_slug.replace("-", " ").title()

    return "Unknown"


def parse_article(html: str, url: str) -> Article:
    """Parse an HTML page into an Article model."""
    soup = BeautifulSoup(html, "lxml")

    # Extract title
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else "Untitled"
    # Clean up common title patterns
    title = re.sub(r"\s*[-|]\s*Answering Islam.*$", "", title)
    title = title.strip()

    # Extract main content (skip nav/sidebar)
    content_div = soup.find("div", class_="content")
    if not content_div:
        # Fallback: try the body, excluding nav
        content_div = soup.find("body")
        if content_div:
            # Remove nav elements
            for nav in content_div.find_all("div", class_="left"):
                nav.decompose()

    if content_div:
        # Remove scripts, styles, nav
        for tag in content_div.find_all(["script", "style", "nav"]):
            tag.decompose()

        # Convert to markdown
        content = md(str(content_div), heading_style="ATX")
        # Clean up whitespace
        content = re.sub(r"\n{3,}", "\n\n", content)
        content = content.strip()
    else:
        content = soup.get_text(separator="\n", strip=True)

    # Extract metadata
    author = infer_author(html, url)
    topic = infer_topic(url)

    return Article(
        url=url,
        title=title,
        author=author,
        topic=topic,
        content=content,
        html=html,
    )


def extract_links(html: str, base_url: str) -> list[str]:
    """Extract internal links from an HTML page."""
    soup = BeautifulSoup(html, "lxml")
    links = set()

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        full_url = urljoin(base_url, href)

        # Only keep internal links
        if full_url.startswith(base_url):
            # Normalize: remove fragments, trailing slashes
            full_url = full_url.split("#")[0].rstrip("/")
            # Only keep .html and .htm pages
            if full_url.endswith((".html", ".htm")):
                # Skip non-English language sections
                if any(excluded in full_url for excluded in EXCLUDED_PATHS):
                    continue
                links.add(full_url)

    return list(links)
