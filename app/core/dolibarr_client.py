import time
import requests
from typing import Optional, Dict, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.config import DOLIBARR_API, DOLIBARR_KEY, MAX_RETRIES, RETRY_BACKOFF_FACTOR, REQUEST_TIMEOUT
from app.utils.logger import logger


class DolibarrClient:
    """Dolibarr API client with retry logic and error handling."""

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        self.base_url = base_url or DOLIBARR_API
        self.api_key = api_key or DOLIBARR_KEY
        self.session = requests.Session()

        retry_strategy = Retry(
            total=MAX_RETRIES,
            backoff_factor=RETRY_BACKOFF_FACTOR,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _get_headers(self) -> Dict[str, str]:
        """Get common headers for requests."""
        return {
            "DOLAPIKEY": self.api_key,
            "Content-Type": "application/json"
        }

    def _handle_response(self, response: requests.Response) -> Any:
        """Handle API response and errors."""
        if response.status_code == 401:
            logger.error("Dolibarr authentication failed - invalid API key")
            raise Exception("Dolibarr authentication failed")

        if response.status_code == 404:
            logger.warning("Dolibarr resource not found")
            return None

        if response.status_code >= 400:
            logger.error(f"Dolibarr error: {response.status_code} - {response.text}")
            response.raise_for_status()

        if response.status_code == 204:
            return {"success": True}

        try:
            return response.json()
        except ValueError:
            return {"success": True, "raw": response.text}

    def request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Any:
        """Make HTTP request to Dolibarr API with retry logic."""
        url = f"{self.base_url}/{endpoint}" if not endpoint.startswith("http") else endpoint

        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=self._get_headers(),
                    timeout=REQUEST_TIMEOUT
                )
                return self._handle_response(response)

            except requests.exceptions.Timeout:
                logger.warning(f"Dolibarr request timeout, attempt {attempt + 1}/{MAX_RETRIES}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_BACKOFF_FACTOR ** attempt)
                else:
                    raise

            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Dolibarr connection error: {e}, attempt {attempt + 1}/{MAX_RETRIES}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_BACKOFF_FACTOR ** attempt)
                else:
                    raise

            except requests.exceptions.RequestException as e:
                logger.error(f"Dolibarr request error: {e}")
                raise

        raise Exception("Max retries exceeded for Dolibarr request")

    def post(self, endpoint: str, data: Dict[str, Any]) -> Any:
        """POST data to Dolibarr API."""
        logger.info(f"Sending data to Dolibarr: {endpoint}")
        return self.request("POST", endpoint, data=data)

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """GET data from Dolibarr API."""
        return self.request("GET", endpoint, params=params)

    def put(self, endpoint: str, data: Dict[str, Any]) -> Any:
        """PUT data to Dolibarr API."""
        return self.request("PUT", endpoint, data=data)

    def send_repository(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send repository data to Dolibarr."""
        payload = {
            "name": repo_data.get("name"),
            "full_name": repo_data.get("full_name"),
            "description": repo_data.get("description"),
            "url": repo_data.get("url"),
            "stars": repo_data.get("stars", 0),
            "forks": repo_data.get("forks", 0),
            "language": repo_data.get("language"),
            "owner": repo_data.get("owner"),
        }
        return self.post("repositories", payload)

    def send_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send user/candidate data to Dolibarr."""
        payload = {
            "login": user_data.get("login"),
            "name": user_data.get("name") or user_data.get("login"),
            "email": user_data.get("email"),
            "followers": user_data.get("followers", 0),
            "public_repos": user_data.get("public_repos", 0),
            "languages": user_data.get("languages", []),
            "company": user_data.get("company"),
            "location": user_data.get("location"),
            "bio": user_data.get("bio"),
            "github_url": user_data.get("html_url"),
        }
        return self.post("candidates", payload)

    def send_relationships(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send relationship data to Dolibarr."""
        return self.post("relationships", data)


dolibarr_client = DolibarrClient()
