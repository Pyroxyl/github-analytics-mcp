# MCP Server 主程式
# 負責啟動 MCP server 並註冊所有可用的工具

import asyncio
import json
import os
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    TextContent,
    Tool,
)

from .github_client import (
    GitHubClient,
    GitHubClientError,
    RepositoryNotFoundError,
    AuthenticationError,
    RateLimitError,
)


# 建立 MCP Server 實例
server = Server("github-analytics")

# 建立 GitHub 客戶端實例 (從環境變數讀取 token)
github_client: GitHubClient | None = None


def get_github_client() -> GitHubClient:
    """取得或建立 GitHub 客戶端實例"""
    global github_client
    if github_client is None:
        token = os.environ.get("GITHUB_TOKEN")
        github_client = GitHubClient(token=token)
    return github_client


# 定義所有可用的工具
TOOLS = [
    Tool(
        name="get_repo_stats",
        description="取得 GitHub 倉庫的統計資訊,包含 stars、forks、open issues 和 watchers 數量。"
                    "可用於快速了解一個專案的受歡迎程度和活躍度。",
        inputSchema={
            "type": "object",
            "properties": {
                "owner": {
                    "type": "string",
                    "description": "倉庫擁有者的 GitHub 使用者名稱或組織名稱"
                },
                "repo": {
                    "type": "string",
                    "description": "倉庫名稱"
                }
            },
            "required": ["owner", "repo"]
        }
    ),
    Tool(
        name="list_recent_commits",
        description="列出 GitHub 倉庫最近的 commits 紀錄。"
                    "可指定要取得的 commit 數量,以及可選擇特定分支。"
                    "回傳每個 commit 的 SHA、作者、訊息和時間。",
        inputSchema={
            "type": "object",
            "properties": {
                "owner": {
                    "type": "string",
                    "description": "倉庫擁有者的 GitHub 使用者名稱或組織名稱"
                },
                "repo": {
                    "type": "string",
                    "description": "倉庫名稱"
                },
                "limit": {
                    "type": "integer",
                    "description": "要取得的 commit 數量,預設為 10",
                    "default": 10,
                    "minimum": 1,
                    "maximum": 100
                },
                "branch": {
                    "type": "string",
                    "description": "指定分支名稱,預設為倉庫的預設分支"
                }
            },
            "required": ["owner", "repo"]
        }
    ),
    Tool(
        name="analyze_contributors",
        description="分析 GitHub 倉庫的主要貢獻者。"
                    "回傳貢獻者列表,包含每位貢獻者的 commit 數量、新增和刪除的程式碼行數。"
                    "可用於了解專案的貢獻分布和核心維護者。",
        inputSchema={
            "type": "object",
            "properties": {
                "owner": {
                    "type": "string",
                    "description": "倉庫擁有者的 GitHub 使用者名稱或組織名稱"
                },
                "repo": {
                    "type": "string",
                    "description": "倉庫名稱"
                },
                "top_n": {
                    "type": "integer",
                    "description": "要取得的前 N 名貢獻者,預設為 10",
                    "default": 10,
                    "minimum": 1,
                    "maximum": 100
                }
            },
            "required": ["owner", "repo"]
        }
    ),
    Tool(
        name="get_language_breakdown",
        description="取得 GitHub 倉庫的程式語言分布統計。"
                    "回傳每種程式語言的位元組數和百分比。"
                    "可用於了解專案的技術棧組成。",
        inputSchema={
            "type": "object",
            "properties": {
                "owner": {
                    "type": "string",
                    "description": "倉庫擁有者的 GitHub 使用者名稱或組織名稱"
                },
                "repo": {
                    "type": "string",
                    "description": "倉庫名稱"
                }
            },
            "required": ["owner", "repo"]
        }
    ),
]


@server.list_tools()
async def list_tools() -> list[Tool]:
    """回傳所有可用的工具列表"""
    return TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> CallToolResult:
    """處理工具呼叫請求"""
    try:
        if name == "get_repo_stats":
            result = await handle_get_repo_stats(arguments)
        elif name == "list_recent_commits":
            result = await handle_list_recent_commits(arguments)
        elif name == "analyze_contributors":
            result = await handle_analyze_contributors(arguments)
        elif name == "get_language_breakdown":
            result = await handle_get_language_breakdown(arguments)
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"未知的工具: {name}")],
                isError=True
            )

        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        )

    except ValueError as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"參數錯誤: {str(e)}")],
            isError=True
        )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"執行錯誤: {str(e)}")],
            isError=True
        )


async def handle_get_repo_stats(arguments: dict[str, Any]) -> dict[str, Any]:
    """處理 get_repo_stats 工具"""
    owner = arguments.get("owner")
    repo = arguments.get("repo")

    if not owner or not repo:
        raise ValueError("owner 和 repo 為必要參數")

    try:
        client = get_github_client()
        stats = client.get_repo_statistics(owner, repo)
        return {
            "repository": f"{owner}/{repo}",
            "stats": {
                "stars": stats["stars"],
                "forks": stats["forks"],
                "open_issues": stats["open_issues"],
                "watchers": stats["watchers"],
            },
            "description": stats["description"],
            "language": stats["language"],
            "created_at": stats["created_at"],
            "updated_at": stats["updated_at"],
            "default_branch": stats["default_branch"],
        }
    except RepositoryNotFoundError:
        return {"error": "Repository not found"}
    except AuthenticationError:
        return {"error": "Authentication failed. Check your GitHub token"}
    except RateLimitError:
        return {"error": "GitHub API rate limit exceeded"}
    except GitHubClientError as e:
        return {"error": str(e)}


async def handle_list_recent_commits(arguments: dict[str, Any]) -> dict[str, Any]:
    """處理 list_recent_commits 工具"""
    owner = arguments.get("owner")
    repo = arguments.get("repo")
    limit = arguments.get("limit", 10)
    branch = arguments.get("branch")

    if not owner or not repo:
        raise ValueError("owner 和 repo 為必要參數")

    if not isinstance(limit, int) or limit < 1 or limit > 100:
        raise ValueError("limit 必須是 1-100 之間的整數")

    try:
        client = get_github_client()
        commits = client.get_recent_commits(owner, repo, limit=limit, branch=branch)
        return {
            "repository": f"{owner}/{repo}",
            "branch": branch or "default",
            "limit": limit,
            "commits": commits,
        }
    except RepositoryNotFoundError:
        return {"error": "Repository not found"}
    except AuthenticationError:
        return {"error": "Authentication failed. Check your GitHub token"}
    except RateLimitError:
        return {"error": "GitHub API rate limit exceeded"}
    except GitHubClientError as e:
        return {"error": str(e)}


async def handle_analyze_contributors(arguments: dict[str, Any]) -> dict[str, Any]:
    """處理 analyze_contributors 工具"""
    owner = arguments.get("owner")
    repo = arguments.get("repo")
    top_n = arguments.get("top_n", 10)

    if not owner or not repo:
        raise ValueError("owner 和 repo 為必要參數")

    if not isinstance(top_n, int) or top_n < 1 or top_n > 100:
        raise ValueError("top_n 必須是 1-100 之間的整數")

    try:
        client = get_github_client()
        contributors = client.get_contributors_stats(owner, repo, top_n=top_n)
        return {
            "repository": f"{owner}/{repo}",
            "top_n": top_n,
            "contributors": contributors,
        }
    except RepositoryNotFoundError:
        return {"error": "Repository not found"}
    except AuthenticationError:
        return {"error": "Authentication failed. Check your GitHub token"}
    except RateLimitError:
        return {"error": "GitHub API rate limit exceeded"}
    except GitHubClientError as e:
        return {"error": str(e)}


async def handle_get_language_breakdown(arguments: dict[str, Any]) -> dict[str, Any]:
    """處理 get_language_breakdown 工具"""
    owner = arguments.get("owner")
    repo = arguments.get("repo")

    if not owner or not repo:
        raise ValueError("owner 和 repo 為必要參數")

    try:
        client = get_github_client()
        languages = client.get_languages(owner, repo)
        return {
            "repository": f"{owner}/{repo}",
            "languages": languages,
        }
    except RepositoryNotFoundError:
        return {"error": "Repository not found"}
    except AuthenticationError:
        return {"error": "Authentication failed. Check your GitHub token"}
    except RateLimitError:
        return {"error": "GitHub API rate limit exceeded"}
    except GitHubClientError as e:
        return {"error": str(e)}


async def main():
    """啟動 MCP Server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
