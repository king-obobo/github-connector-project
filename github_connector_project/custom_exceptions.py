

class GitHubApiError(Exception):
    """Custom exception for GitHub API errors."""
    pass


class ResourceNotFound(GitHubApiError):
    """Exception raised when a requested resource is not found."""
    pass


class AuthenticationError(GitHubApiError):
    """Exception raised for authentication failures."""
    pass


class ServerError(GitHubApiError):
    """Exception raised for server-side errors (5xx)."""
    pass

class InvalidRequest(GitHubApiError):
    """Exception raised for invalid API requests."""
    pass


class MaxRetriesExceeded(GitHubApiError):
    """Exception raised when maximum retry attempts are exceeded."""
    pass