import time
import requests
from typing import Optional, Dict, Any, List
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.config import GITHUB_TOKENS, GITHUB_API_BASE, MAX_RETRIES, RETRY_BACKOFF_FACTOR, REQUEST_TIMEOUT
from app.utils.logger import logger


class TokenManager:
    """Manages GitHub API tokens with quota tracking and rotation."""

    def __init__(self, tokens: List[str]):
        self.tokens = {token: {"quota": 5000, "remaining": 5000, "reset_time": 0, "disabled": False} for token in tokens}
        self.available_tokens = list(self.tokens.keys())
        self.current_index = 0

    def get_token(self) -> Optional[str]:
        """Get next available token with remaining quota."""
        attempts = 0
        while attempts < len(self.tokens):
            if not self.available_tokens:
                return None

            token = self.available_tokens[self.current_index % len(self.available_tokens)]
            self.current_index += 1

            token_info = self.tokens.get(token)
            if token_info and not token_info["disabled"]:
                if token_info["remaining"] > 0:
                    return token

            attempts += 1

        return None

    def update_token_status(self, token: str, remaining: int, reset_time: int):
        """Update token quota and status based on API response."""
        if token in self.tokens:
            self.tokens[token]["remaining"] = remaining
            self.tokens[token]["reset_time"] = reset_time

            if remaining == 0:
                self.tokens[token]["disabled"] = True
                if token in self.available_tokens:
                    self.available_tokens.remove(token)
                logger.warning(f"Token disabled due to rate limit. Reset at {reset_time}")

    def reenable_token(self, token: str):
        """Re-enable a token after its rate limit reset."""
        if token in self.tokens:
            self.tokens[token]["disabled"] = False
            self.tokens[token]["remaining"] = 5000
            if token not in self.available_tokens:
                self.available_tokens.append(token)
            logger.info(f"Token re-enabled: {token[:4]}...")

    def check_reset_times(self):
        """Check if any disabled tokens can be re-enabled."""
        current_time = time.time()
        for token, info in self.tokens.items():
            if info["disabled"] and info["reset_time"] <= current_time:
                self.reenable_token(token)


token_manager = TokenManager(GITHUB_TOKENS)


class GitHubClient:
    """GitHub API client with automatic token rotation and retry logic."""

    BASE_URL = GITHUB_API_BASE

    def __init__(self):
        self.session = requests.Session()
        retry_strategy = Retry(
            total=MAX_RETRIES,
            backoff_factor=RETRY_BACKOFF_FACTOR,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _make_request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make HTTP request with token rotation and retry logic."""
        token = token_manager.get_token()

        if not token:
            token_manager.check_reset_times()
            time.sleep(60)
            token = token_manager.get_token()
            if not token:
                raise Exception("No available GitHub tokens")

        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        url = f"{self.BASE_URL}{endpoint}"

        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data,
                    headers=headers,
                    timeout=REQUEST_TIMEOUT
                )

                remaining = int(response.headers.get("X-RateLimit-Remaining", 5000))
                reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
                token_manager.update_token_status(token, remaining, reset_time)

                if response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        logger.warning(f"Rate limit hit. Retry after {reset_time}")
                        token_manager.tokens[token]["disabled"] = True
                        if token in token_manager.available_tokens:
                            token_manager.available_tokens.remove(token)

                        token = token_manager.get_token()
                        if token:
                            headers["Authorization"] = f"Bearer {token}"
                            continue
                    raise Exception(f"Forbidden: {response.text}")

                if response.status_code == 404:
                    return {}

                if response.status_code >= 500:
                    logger.warning(f"Server error {response.status_code}, attempt {attempt + 1}")
                    time.sleep(RETRY_BACKOFF_FACTOR ** attempt)
                    continue

                response.raise_for_status()
                return response.json()

            except requests.exceptions.RequestException as e:
                logger.error(f"Request error: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_BACKOFF_FACTOR ** attempt)
                else:
                    raise

        raise Exception("Max retries exceeded")

    def search_repositories(self, query: str, page: int = 1, per_page: int = 100) -> Dict[str, Any]:
        """Search repositories by query."""
        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": per_page,
            "page": page
        }
        return self._make_request("GET", "/search/repositories", params=params)

    def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get repository details."""
        return self._make_request("GET", f"/repos/{owner}/{repo}")

    def get_repo_contributors(self, owner: str, repo: str, page: int = 1, per_page: int = 100) -> List[Dict[str, Any]]:
        """Get contributors of a repository."""
        params = {"page": page, "per_page": per_page}
        result = self._make_request("GET", f"/repos/{owner}/{repo}/contributors", params=params)
        return result if isinstance(result, list) else []

    def get_user(self, username: str) -> Dict[str, Any]:
        """Get user details."""
        return self._make_request("GET", f"/users/{username}")

    def get_user_repos(self, username: str, page: int = 1, per_page: int = 100) -> List[Dict[str, Any]]:
        """Get user repositories."""
        params = {"page": page, "per_page": per_page, "sort": "updated"}
        result = self._make_request("GET", f"/users/{username}/repos", params=params)
        return result if isinstance(result, list) else []


github_client = GitHubClient()
