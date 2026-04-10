import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://bot:botpass@localhost:5432/githubminer")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

GITHUB_TOKENS: List[str] = [t.strip() for t in os.getenv("GITHUB_TOKENS", "").split(",") if t.strip()]
GITHUB_API_BASE = "https://api.github.com"

DOLIBARR_API = os.getenv("DOLIBARR_API", "")
DOLIBARR_KEY = os.getenv("DOLIBARR_KEY", "")

MAX_RETRIES = 3
RETRY_BACKOFF_FACTOR = 2
REQUEST_TIMEOUT = 30

PER_PAGE = 100
MAX_PAGES = 10
