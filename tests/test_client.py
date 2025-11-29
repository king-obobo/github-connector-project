import pytest
from github_connector_project.client import GitHubClient
from github_connector_project.custom_exceptions import (
    AuthenticationError, ResourceNotFound,
    GitHubApiError, InvalidRequest,
    MaxRetriesExceeded, ServerError
)
from unittest.mock import patch, MagicMock


# Starting from the very beginning
def test_client_initializes_with_token():
    client = GitHubClient("test-token")
    assert client.token == "test-token"
    assert "Authorization" in client.session.headers


def test_client_raises_error_without_token():
    with pytest.raises(AuthenticationError):
        GitHubClient(token=None)


@patch("github_connector_project.client.requests.Session.request")
def test_make_request_success(mock_request):
    mock_response = MagicMock(status_code = 200)
    mock_response.json.return_value = {"message": "ok"}
    mock_request.return_value = mock_response

    client = GitHubClient("123")
    response = client._make_request("GET", "/rate_limit")

    assert response == {"message": "ok"}


@patch("github_connector_project.client.requests.Session.request")
def test_404_raises_resource_not_found(mock_request):
    mock_response = MagicMock(status_code=404)
    mock_request.return_value = mock_response

    client = GitHubClient("123")

    with pytest.raises(ResourceNotFound):
        client._make_request("GET", "/invalid")


@patch("github_connector_project.client.time.sleep", return_value=None)
@patch("github_connector_project.client.requests.Session.request")
def test_rate_limit_then_success(mock_request, mock_sleep):
    rate_limit_response = MagicMock(status_code=429, headers={"Retry-After": "1"})
    success_response = MagicMock(status_code=200, json=lambda: {"ok": True})

    mock_request.side_effect = [rate_limit_response, success_response]

    client = GitHubClient("123")

    res = client._make_request("GET", "/repos/me/app")

    assert res == {"ok": True}
    assert mock_sleep.called
    
    

@patch("github_connector_project.client.time.sleep")
@patch("github_connector_project.client.requests.Session.request")
def test_server_error_retries_then_fails(mock_request, _):
    responses = [MagicMock(status_code=500) for _ in range(6)]
    mock_request.side_effect = responses

    client = GitHubClient("123")

    with pytest.raises(ServerError):
        client._make_request("GET", "/something")



@patch("github_connector_project.client.GitHubClient._make_request")
def test_get_repo_details(mock_make):
    mock_make.return_value = {
        "name": "sample",
        "created_at": "2020",
        "description": "desc",
        "forks_count": 10,
        "homepage": "https://x.com",
        "language": "Python",
        "private": False,
        "stargazers_count": 5,
        "subscribers_count": 2,
        "updated_at": "2024",
        "watchers_count": 7,
    }

    client = GitHubClient("123")
    result = client.get_repo_details("me", "sample")

    assert result["repo_name"] == "sample"
    assert "repo_no_of_stars" in result
