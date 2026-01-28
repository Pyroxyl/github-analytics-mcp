"""Pydantic models for API request/response schemas."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "github-analytics-api"


class RepoStatsResponse(BaseModel):
    repository: str
    stars: int
    forks: int
    open_issues: int
    watchers: int
    description: str
    language: str
    created_at: str
    updated_at: str
    default_branch: str


class CommitItem(BaseModel):
    sha: str
    message: str
    author: str
    author_login: str
    date: str
    url: str


class CommitsResponse(BaseModel):
    repository: str
    branch: str
    limit: int
    commits: list[CommitItem]


class ContributorItem(BaseModel):
    login: str
    contributions: int
    avatar_url: str
    profile_url: str


class ContributorsResponse(BaseModel):
    repository: str
    top_n: int
    contributors: list[ContributorItem]


class LanguagesResponse(BaseModel):
    repository: str
    languages: dict[str, float]


class ErrorResponse(BaseModel):
    error: str
    detail: str = ""
