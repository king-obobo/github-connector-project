from .logger import setup_logger
import time
import requests
import random
from typing import Optional, Dict, Any
from .custom_exceptions import (
    GitHubApiError, ResourceNotFound, AuthenticationError,
    InvalidRequest, MaxRetriesExceeded, ServerError
)

logger = setup_logger(__name__)

class GitHubClient:
    """
    A resilient client for interacting with the Github API
    """

    BASE_URL = "https://api.github.com"
    
    def __init__(self,token:str, max_retries: int = 5, base_delay: int = 1, cap: int = 60) -> None:
        
        self.token = token
        
        if not self.token:
            logger.error("GitHub Personal Access Token is required. Missing PAT in the environment variables.")
            raise AuthenticationError("GitHub Personal Access Token is required.")
        
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.cap = cap
        
        # Starting a session for connection pooling
        self.session = requests.Session()
        
        # Setting up headers with authentication
        self.session.headers.update(self._get_headers())
        
        logger.info("GitHubClient initialized successfully.")
        
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Constructs headers for the API requests
        """
        return {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {self.token}",
            "User-Agent": "GitHubClient/1.0"
        }
    
    
    def _exponential_backoff(self, attempt: int) -> None:
        """
        Calculates the delay for exponential backoff and sleeps for that duration
        """
        delay = min(self.cap, self.base_delay * (2 ** attempt))
        jitter = random.uniform(0, delay * 0.1)
        total_sleep = delay + jitter
        
        # Logging the backoff details
        logger.warning(f"[Attempt {attempt}]. Retrying after {total_sleep:.2f} seconds...")
        
        time.sleep(total_sleep)
        
        
    def _send_request(self, method: str, url:str, attempt) -> requests.Response:
        """
        Sends an HTTP request using the session
        returns the response object
        """
        logger.info(f"Making {method} request to {url} | Attempt {attempt + 1}")
        return self.session.request(method, url)
    
    
    def _handle_success(self, status:int, response:requests.Response) -> Dict[str, Any]:
        """
        Handles successful responses
        """
        logger.info(f"Request successful: CODE:{status}")
        return response.json()
    
    
    def _handle_client_errors(self, url:str, response: requests.Response) -> None:
        """
        Handles client-side errors (4xx)
        """
        status = response.status_code
        
        if status == 404:
            logger.error(f"Resource not found: {url}")
            raise ResourceNotFound(f"Resource not found: {url}")
        
        if status == 401:
            logger.error("Authentication failed. Check your GitHub token.")
            raise AuthenticationError("Authentication failed. Check your GitHub token.")
        
        
    def _get_rate_limit_wait_time(self, response: requests.Response) -> Optional[int]:
        """
        Extracts the wait time from rate limit headers if available or the reset time
        """
        retry_after = response.headers.get("Retry-After")
        
        if retry_after:
            return float(retry_after) + random.uniform(0, 1)
        
        reset = response.headers.get("X-RateLimit-Reset")
        if reset:
            reset_time = int(reset)
            current_time = int(time.time())
            return max(0, reset_time - current_time)  
        
        
    def _handle_rate_limit(self, response: requests.Response, attempt: int):
        """
        Handles the rate limits

        Args:
            response (requests.Response): The response object
            attempt (int): Number of attempts so far

        Raises:
            MaxRetriesExceeded: The error is raised when max retries > attempts
        """
        wait = self._get_rate_limit_wait_time(response)
        
        if wait:
            logger.warning("Rate limit hit. Waiting {wait:.2f} seconds...")
            time.sleep(wait)
            
        else:
            self._exponential_backoff(attempt)
            
        if attempt > self.max_retries:
            logger.error("Rate Limit exceeded...")
            raise MaxRetriesExceeded("Rate Limit retries exceeded...")
        
        
    def _handle_server_error(self, response: requests.Response, attempt: int) -> None:
        if attempt >= self.max_retries:
            logger.warning(f"Server error {response.status_code}. Max retries exceeded")
            raise ServerError(f"Server error {response.status_code}. Max retries exceeded.")
        
        self._exponential_backoff(attempt)
        
        
        
    def _make_request(self, method: str, endpoint: str) -> Any:
        """
        Makes an API request with retries and error handling
        """
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        
        attempt = 0
        
        while True:
            response = self._send_request(method, url, attempt)
            status = response.status_code
            
            # Status code handling
            if 200 <= status < 300:
                return self._handle_success(status, response)
            
            if status == 404 or status == 401:
                self._handle_client_errors(url, response)
            
            if status == 429 or (status == 403 and response.headers.get("X-RateLimit-Remaining") == "0"):
                self._handle_rate_limit(response, attempt)
                attempt += 1
                continue
                            
            if 500 <= status < 600:
                self._handle_server_error(response, attempt)
                attempt += 1
                continue
            
            if 400 <= status < 500:
                logger.error(f"Invalid request: {status} - {response.text}")
                raise InvalidRequest(f"Invalid request: {status} - {response.text}")
            
            raise GitHubApiError(f"Unexpected error: {status} - {response.text}")
        
        
    def get_repo_details(self, owner: str, repo: str) -> Any:
        """Fetch details of a specific repository"""
        
        endpoint = f"repos/{owner}/{repo}"
        json_obj = self._make_request("GET", endpoint)
        
        repo_details = {
            "repo_name" : json_obj.get("name"),
            "repo_creation_time" : json_obj.get("created_at"),
            "repo_description" : json_obj.get("description"),
            "repo_fork_count" : json_obj.get("forks_count"),
            "repo_homepage_url" : json_obj.get("homepage"),
            "repo_language" : json_obj.get("language"),
            "repo_homepage_url" : json_obj.get("homepage"),
            "repo_is_private" : json_obj.get("private"),
            "repo_no_of_stars" : json_obj.get("stargazers_count"),
            "repo_no_of_subs" : json_obj.get("subscribers_count"),
            "repo_last_update" : json_obj.get("updated_at"),
            "repo_watchers" : json_obj.get("watchers_count"),
        }
        
        return repo_details