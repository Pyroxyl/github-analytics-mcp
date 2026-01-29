"""FastAPI dependencies for dependency injection."""

import os
import sys
from functools import lru_cache

# Add project root to path so we can import from src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.github_client import GitHubClient


# WHY @lru_cache as singleton: FastAPI calls dependency functions on every request.
# lru_cache ensures only one GitHubClient (and one PyGithub connection) exists,
# avoiding redundant token validation and object creation. No need for a DI
# container — the stdlib does the job.
@lru_cache()
def get_github_client() -> GitHubClient:
    """Create and cache a GitHubClient instance."""
    token = os.environ.get("GITHUB_TOKEN")
    return GitHubClient(token=token)
