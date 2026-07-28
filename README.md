# Answering Islam RAG

A Christian apologetics web application that crawls [answering-islam.org](https://www.answering-islam.org), stores content in a vector database, and lets you ask questions answered by the site's content with source citations.

## Features

- 🔍 **Semantic Search** — Find relevant articles by meaning, not just keywords
- 💬 **RAG Chatbot** — Ask questions and get answers sourced from the site
- 📚 **Source Citations** — Every answer links back to the original article
- 🎯 **Topic Filtering** — Focus searches on specific areas (Qur'an, Jesus, Bible, etc.)
- ⚡ **Local Embeddings** — No API key required for search (uses sentence-transformers)
- 🔄 **Resumable Crawl** — Pause and resume crawling without losing progress

## Quick Start

### Prerequisites

- Python 3.11+
- pip

### Setup

```bash
# Clone the repo
git clone https://github.com/williamlim16/answering-islam-ai.git
cd answering-islam-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -e .
```

### Step 1: Crawl the Site

```bash
python scripts/crawl.py
```

This crawls answering-islam.org (takes ~30-60 minutes for the full site).

You can limit the crawl for testing:

```bash
# Crawl only 5 pages
python scripts/crawl.py --max-pages 5

# Custom delay between requests (be polite!)
python scripts/crawl.py --delay 2.0

# Start from a specific URL
python scripts/crawl.py --start "https://www.answering-islam.org/Quran/"
```

The crawler saves raw HTML to `data/raw/` and creates a `manifest.json` for resume support. If interrupted, just run `python scripts/crawl.py` again — it picks up where it left off.

### Step 2: Build the Index (coming in Phase 2)

```bash
python scripts/index.py
```

This processes the crawled content into a searchable vector index.

### Step 3: Start the Server (coming in Phase 3)

```bash
python scripts/serve.py
```

Open http://localhost:8000 in your browser.

## Project Structure

```
answering-islam-ai/
├── README.md
├── requirements.txt
├── pyproject.toml
├── .env.example
├── config.py                  # App configuration
├── src/
│   ├── crawler/
│   │   ├── models.py          # Article & Chunk Pydantic models
│   │   ├── parser.py          # HTML → clean markdown
│   │   └── scraper.py         # BFS web crawler
│   ├── index/                 # Phase 2: chunking, embeddings, vector store
│   ├── api/                   # Phase 3: FastAPI backend
│   └── web/                   # Phase 3: HTML templates
├── scripts/
│   └── crawl.py               # CLI: run the crawler
├── data/
│   ├── raw/                   # Crawled HTML files
│   └── processed/             # Cleaned markdown chunks
└── tests/
    ├── test_models.py
    └── test_parser.py
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Crawler | BeautifulSoup4, requests, markdownify |
| Data Models | Pydantic v2 |
| Text Processing | markdownify, lxml |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector DB | ChromaDB |
| Backend | FastAPI, uvicorn |
| Frontend | Vanilla HTML/CSS/JS |
| LLM (optional) | OpenAI GPT-4o-mini |

## Configuration

All settings are in `config.py`. Key options:

| Setting | Default | Description |
|---------|---------|-------------|
| `BASE_URL` | `https://www.answering-islam.org` | Site to crawl |
| `CRAWL_DELAY` | `1.5` | Seconds between requests |
| `MAX_PAGES` | `2000` | Safety limit for crawling |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Local embedding model |
| `CHUNK_SIZE` | `1000` | Characters per chunk |
| `CHUNK_OVERLAP` | `200` | Overlap between chunks |

Override via environment variables or `.env` file:

```bash
cp .env.example .env
# Edit .env with your settings
```

## Development

### Run Tests

```bash
pip install pytest
pytest tests/ -v
```

### Project Phases

- [x] **Phase 1: Crawler Pipeline** — Project setup, HTML parser, BFS crawler, CLI scripts
- [ ] **Phase 2: Vector Index** — Text chunking, embeddings, ChromaDB vector store
- [ ] **Phase 3: Web Application** — FastAPI backend, RAG endpoint, chat UI
- [ ] **Phase 4: Polish & Ship** — README, docs, incremental crawl, topic filtering, Docker

## License

MIT
