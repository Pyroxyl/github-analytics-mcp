"""API route definitions."""

from fastapi import APIRouter, Depends, HTTPException, Query

from src.github_client import (
    GitHubClient,
    GitHubClientError,
    RepositoryNotFoundError,
    AuthenticationError,
    RateLimitError,
)

from .dependencies import get_github_client
from .models import (
    RepoStatsResponse,
    CommitsResponse,
    ContributorsResponse,
    LanguagesResponse,
)

router = APIRouter(prefix="/api/v1")


def handle_github_error(e: GitHubClientError):
    """Convert GitHubClientError to HTTPException."""
    if isinstance(e, RepositoryNotFoundError):
        raise HTTPException(status_code=404, detail=str(e))
    elif isinstance(e, AuthenticationError):
        raise HTTPException(status_code=401, detail=str(e))
    elif isinstance(e, RateLimitError):
        raise HTTPException(status_code=429, detail=str(e))
    else:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/repo/{owner}/{repo}/stats", response_model=RepoStatsResponse)
def get_repo_stats(
    owner: str,
    repo: str,
    client: GitHubClient = Depends(get_github_client),
):
    """Get repository statistics."""
    try:
        stats = client.get_repo_statistics(owner, repo)
        return RepoStatsResponse(
            repository=f"{owner}/{repo}",
            **stats,
        )
    except GitHubClientError as e:
        handle_github_error(e)


@router.get("/repo/{owner}/{repo}/commits", response_model=CommitsResponse)
def get_commits(
    owner: str,
    repo: str,
    limit: int = Query(default=10, ge=1, le=100),
    branch: str | None = Query(default=None),
    client: GitHubClient = Depends(get_github_client),
):
    """Get recent commits."""
    try:
        commits = client.get_recent_commits(owner, repo, limit=limit, branch=branch)
        return CommitsResponse(
            repository=f"{owner}/{repo}",
            branch=branch or "default",
            limit=limit,
            commits=commits,
        )
    except GitHubClientError as e:
        handle_github_error(e)


@router.get("/repo/{owner}/{repo}/contributors", response_model=ContributorsResponse)
def get_contributors(
    owner: str,
    repo: str,
    top_n: int = Query(default=10, ge=1, le=100),
    client: GitHubClient = Depends(get_github_client),
):
    """Get top contributors."""
    try:
        contributors = client.get_contributors_stats(owner, repo, top_n=top_n)
        return ContributorsResponse(
            repository=f"{owner}/{repo}",
            top_n=top_n,
            contributors=contributors,
        )
    except GitHubClientError as e:
        handle_github_error(e)


@router.get("/repo/{owner}/{repo}/languages", response_model=LanguagesResponse)
def get_languages(
    owner: str,
    repo: str,
    client: GitHubClient = Depends(get_github_client),
):
    """Get language breakdown."""
    try:
        languages = client.get_languages(owner, repo)
        return LanguagesResponse(
            repository=f"{owner}/{repo}",
            languages=languages,
        )
    except GitHubClientError as e:
        handle_github_error(e)
