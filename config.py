"""Application configuration."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
CHROMA_DIR = DATA_DIR / "chromadb"

# Crawler settings
BASE_URL = "https://www.answering-islam.org"
CRAWL_DELAY = 1.5  # seconds between requests per worker
MAX_PAGES = 2000  # safety limit
REQUEST_TIMEOUT = 30  # seconds
CRAWL_CONCURRENCY = 5  # number of concurrent workers

# Language filter — excluded URL path prefixes (non-English sections)
EXCLUDED_PATHS = [
    "/Arabic/",
    "/arabic/",
    "/chinese/",
    "/Chinese/",
    "/Dutch/",
    "/dutch/",
    "/French/",
    "/french/",
    "/indonesian/",
    "/Indonesian/",
    "/Bahasa/",
    "/bahasa/",
    "/russian/",
    "/Russian/",
    "/Urdu/",
    "/urdu/",
    "/persian/",
    "/Persian/",
    "/turkish/",
    "/Turkish/",
    "/portuguese/",
    "/Portuguese/",
    "/italian/",
    "/Italian/",
    "/japanese/",
    "/Japanese/",
    "/korean/",
    "/Korean/",
    "/spanish/",
    "/Spanish/",
    "/german/",
    "/German/",
]

# Embedding settings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # fast, local, good quality
CHUNK_SIZE = 1000  # characters per chunk
CHUNK_OVERLAP = 200  # overlap between chunks

# API settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
TOP_K_RESULTS = 5  # default number of results to return

# LLM settings (for RAG answer generation — optional for MVP)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
