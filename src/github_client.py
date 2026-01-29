# GitHub API 客戶端
# 封裝 GitHub REST API 的呼叫邏輯
#
# WHY a wrapper instead of using PyGithub directly: Callers should not know we
# use PyGithub or that GitHub returns HTTP status codes. This class translates
# raw API errors into semantic domain exceptions (RepositoryNotFoundError, etc.)
# so both the MCP server and FastAPI gateway can handle errors without parsing
# status codes. See docs/adr/ADR-002-exception-hierarchy.md.

import os
from typing import Optional

from github import Github, GithubException
from github.Repository import Repository


class GitHubClientError(Exception):
    """GitHub 客戶端錯誤基類"""

    pass


class RepositoryNotFoundError(GitHubClientError):
    """倉庫不存在"""

    pass


class AuthenticationError(GitHubClientError):
    """認證失敗"""

    pass


class RateLimitError(GitHubClientError):
    """API 速率限制"""

    pass


class GitHubClient:
    """GitHub API 客戶端封裝

    使用 PyGithub 套件與 GitHub API 互動,提供倉庫統計、
    commits、貢獻者等資訊的查詢功能。

    Attributes:
        _github: PyGithub 的 Github 實例
    """

    def __init__(self, token: Optional[str] = None):
        """初始化 GitHub 客戶端

        Args:
            token: GitHub Personal Access Token。
                   若未提供,將從環境變數 GITHUB_TOKEN 讀取。

        Raises:
            AuthenticationError: 當 token 無效或未提供時
        """
        self._token = token or os.environ.get("GITHUB_TOKEN")
        if not self._token:
            raise AuthenticationError(
                "GitHub token is required. Set GITHUB_TOKEN environment variable "
                "or pass token to constructor."
            )
        self._github = Github(self._token)

    def _handle_github_exception(self, e: GithubException, owner: str, repo: str):
        """處理 GitHub API 例外

        Args:
            e: GithubException 實例
            owner: 倉庫擁有者
            repo: 倉庫名稱

        Raises:
            RepositoryNotFoundError: 404 錯誤
            AuthenticationError: 401/403 錯誤
            RateLimitError: 速率限制錯誤
            GitHubClientError: 其他錯誤
        """
        if e.status == 404:
            raise RepositoryNotFoundError(f"Repository '{owner}/{repo}' not found")
        elif e.status == 401:
            raise AuthenticationError("Invalid GitHub token")
        elif e.status == 403:
            if "rate limit" in str(e.data).lower():
                raise RateLimitError("GitHub API rate limit exceeded")
            raise AuthenticationError(
                f"Access denied to repository '{owner}/{repo}'"
            )
        else:
            raise GitHubClientError(f"GitHub API error: {e.data}")

    def get_repository(self, owner: str, repo: str) -> Repository:
        """取得倉庫物件

        Args:
            owner: 倉庫擁有者 (使用者名稱或組織名稱)
            repo: 倉庫名稱

        Returns:
            Repository: PyGithub 的 Repository 物件

        Raises:
            RepositoryNotFoundError: 倉庫不存在
            AuthenticationError: 認證失敗或無權限存取
            RateLimitError: API 速率限制
            GitHubClientError: 其他 API 錯誤
        """
        try:
            return self._github.get_repo(f"{owner}/{repo}")
        except GithubException as e:
            self._handle_github_exception(e, owner, repo)

    def get_repo_statistics(self, owner: str, repo: str) -> dict:
        """取得倉庫基本統計資訊

        Args:
            owner: 倉庫擁有者
            repo: 倉庫名稱

        Returns:
            dict: 包含以下欄位的字典:
                - stars (int): Star 數量
                - forks (int): Fork 數量
                - open_issues (int): 開啟的 Issue 數量
                - watchers (int): Watcher 數量
                - description (str): 倉庫描述
                - language (str): 主要程式語言
                - created_at (str): 建立時間 (ISO 格式)
                - updated_at (str): 最後更新時間 (ISO 格式)
                - default_branch (str): 預設分支

        Raises:
            RepositoryNotFoundError: 倉庫不存在
            AuthenticationError: 認證失敗
            GitHubClientError: 其他 API 錯誤
        """
        repository = self.get_repository(owner, repo)

        return {
            "stars": repository.stargazers_count,
            "forks": repository.forks_count,
            "open_issues": repository.open_issues_count,
            "watchers": repository.subscribers_count,
            "description": repository.description or "",
            "language": repository.language or "",
            "created_at": repository.created_at.isoformat() if repository.created_at else "",
            "updated_at": repository.updated_at.isoformat() if repository.updated_at else "",
            "default_branch": repository.default_branch,
        }

    def get_recent_commits(
        self,
        owner: str,
        repo: str,
        limit: int = 10,
        branch: Optional[str] = None,
    ) -> list[dict]:
        """取得最近的 commits

        Args:
            owner: 倉庫擁有者
            repo: 倉庫名稱
            limit: 回傳的 commit 數量上限,預設 10
            branch: 指定分支名稱,若為 None 則使用預設分支

        Returns:
            list[dict]: Commit 資訊列表,每個 commit 包含:
                - sha (str): Commit SHA
                - message (str): Commit 訊息
                - author (str): 作者名稱
                - author_login (str): 作者 GitHub 帳號 (若有)
                - date (str): Commit 日期 (ISO 格式)
                - url (str): Commit 的 GitHub URL

        Raises:
            RepositoryNotFoundError: 倉庫不存在
            AuthenticationError: 認證失敗
            GitHubClientError: 其他 API 錯誤
        """
        repository = self.get_repository(owner, repo)

        # 若未指定分支,使用預設分支
        sha = branch if branch else repository.default_branch

        try:
            commits = repository.get_commits(sha=sha)
        except GithubException as e:
            self._handle_github_exception(e, owner, repo)

        result = []
        for commit in commits[:limit]:
            commit_data = {
                "sha": commit.sha,
                "message": commit.commit.message,
                "author": commit.commit.author.name if commit.commit.author else "Unknown",
                "author_login": commit.author.login if commit.author else "",
                "date": commit.commit.author.date.isoformat() if commit.commit.author else "",
                "url": commit.html_url,
            }
            result.append(commit_data)

        return result

    def get_contributors_stats(
        self, owner: str, repo: str, top_n: int = 10
    ) -> list[dict]:
        """取得貢獻者統計資訊

        Args:
            owner: 倉庫擁有者
            repo: 倉庫名稱
            top_n: 回傳前 N 名貢獻者,預設 10

        Returns:
            list[dict]: 貢獻者資訊列表 (按貢獻數排序),每個貢獻者包含:
                - login (str): GitHub 帳號
                - contributions (int): 貢獻次數 (commits)
                - avatar_url (str): 頭像 URL
                - profile_url (str): GitHub 個人頁面 URL

        Raises:
            RepositoryNotFoundError: 倉庫不存在
            AuthenticationError: 認證失敗
            GitHubClientError: 其他 API 錯誤
        """
        repository = self.get_repository(owner, repo)

        try:
            contributors = repository.get_contributors()
        except GithubException as e:
            self._handle_github_exception(e, owner, repo)

        result = []
        for contributor in contributors[:top_n]:
            result.append({
                "login": contributor.login,
                "contributions": contributor.contributions,
                "avatar_url": contributor.avatar_url,
                "profile_url": contributor.html_url,
            })

        return result

    def get_languages(self, owner: str, repo: str) -> dict:
        """取得倉庫程式語言分布

        Args:
            owner: 倉庫擁有者
            repo: 倉庫名稱

        Returns:
            dict: 語言分布字典,key 為語言名稱,value 為百分比
                  例如: {"Python": 45.2, "JavaScript": 30.1, "TypeScript": 24.7}

        Raises:
            RepositoryNotFoundError: 倉庫不存在
            AuthenticationError: 認證失敗
            GitHubClientError: 其他 API 錯誤
        """
        repository = self.get_repository(owner, repo)

        try:
            languages = repository.get_languages()
        except GithubException as e:
            self._handle_github_exception(e, owner, repo)

        # 計算總 bytes 數
        total_bytes = sum(languages.values())

        if total_bytes == 0:
            return {}

        # 轉換為百分比
        result = {}
        for language, bytes_count in languages.items():
            percentage = round((bytes_count / total_bytes) * 100, 2)
            result[language] = percentage

        return result
