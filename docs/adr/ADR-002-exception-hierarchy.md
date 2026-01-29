# ADR-002: Custom Exception Hierarchy

## Status

Accepted

## Context

The GitHub API communicates errors through HTTP status codes (404, 401, 403, 429) and PyGithub surfaces these as `GithubException` instances with a `.status` attribute. Callers of our client would need to inspect raw HTTP status codes to understand what went wrong — leaking the implementation detail that we use GitHub's REST API.

Both the MCP server and FastAPI gateway need to handle these errors, but they translate them differently:
- MCP: returns user-friendly error text (`"Repository not found"`)
- FastAPI: returns the appropriate HTTP status code (404, 401, 429, 502)

## Decision

Define a custom exception hierarchy in `github_client.py`:

```
GitHubClientError (base)
├── RepositoryNotFoundError  (GitHub 404)
├── AuthenticationError      (GitHub 401, 403 non-rate-limit)
└── RateLimitError           (GitHub 403 rate-limit, 429)
```

`GitHubClient._handle_github_exception()` translates raw `GithubException` instances into these domain-specific exceptions at the boundary. Callers never see `GithubException`.

## Consequences

### Positive

- Callers use semantic `except RepositoryNotFoundError` instead of checking `if e.status == 404`.
- The exception names communicate intent — code reads like documentation.
- Each interface adapter can map exceptions to its own error format without parsing status codes.
- Adding new error types (e.g., `RepositoryArchivedError`) requires no changes to the adapters' catch structure if they already catch the base class.

### Negative

- The mapping in `_handle_github_exception()` is a single point that must be kept in sync with GitHub's API behavior.
- GitHub's 403 status is overloaded (rate limit vs. access denied), requiring string matching on the error message to disambiguate.

### Neutral

- The hierarchy is intentionally flat (one level of inheritance). Deeper hierarchies add complexity without value for four error types.
