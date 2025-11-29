# GitHub Connector Project

## INTRODUCTION
A robust and resilient Python client for interacting with the GitHub REST API v3.
This library abstracts away common concerns such as:

* Authentication

* Error handling

* Exponential backoff

* Rate-limit awareness

* Network resilience

* Clean custom exception types

* Session reuse (connection pooling)

It also ships with a demo script `(main.py)` and a simple test suite using mocks.

### Features

* Requests Session for connection pooling and improved performance.

* Automatic retry logic with exponential backoff + jitter.

* Graceful handling of:

- 4xx client errors

- 5xx server errors

- GitHub Rate Limits (403, 429)

* Easy-to-use API for fetching repository details.

* Custom exceptions for clearer debugging and orchestration-level error handling.

* Poetry-based project with `pyproject.toml` and `poetry.lock`.

## Project Structure
```
github_connector_project/
├── github_connector/          # Package source code
│   ├── __init__.py
│   ├── client.py              # The GitHubClient class
│   └── custom_exceptions.py   # Custom exception classes
├── tests/                     # Unit tests
│   ├── __init__.py
│   └── test_client.py
├── main.py                    # Demo script
├── pyproject.toml             # Poetry config
├── poetry.lock                # Locked dependencies
├── .gitignore
└── README.md
```

## Installation
This project uses Poetry for dependency management.

1. Install Poetry (if not installed)
```
pip install poetry
```

2. Install Dependencies
```
poetry install
```

Poetry will automatically use:

`pyproject.toml` for dependency definitions

`poetry.lock` for exact pinned versions

3. Clone the repo
```
git clone https://github.com/king-obobo/github-connector-project.git
cd github-connector-project
```

4. Run the script
```
poetry run python main.py
```

## Error Handling
The client raises meaningful exceptions

| Exception             | Triggers                  |
| --------------------- | ------------------------- |
| `AuthenticationError` | Invalid or missing token  |
| `ResourceNotFound`    | 404 errors                |
| `InvalidRequest`      | Other 4xx errors          |
| `ServerError`         | GitHub 5xx issues         |
| `MaxRetriesExceeded`  | When retry cap is reached |
| `GitHubApiError`      | Everything else           |
