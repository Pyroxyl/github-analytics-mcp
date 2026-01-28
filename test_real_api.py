#!/usr/bin/env python3
"""測試真實 GitHub API 功能"""

import os
import sys
from dotenv import load_dotenv

# 載入 .env
load_dotenv()

# 添加 src 到 path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from github_client import GitHubClient, GitHubClientError


def print_header(title: str):
    """印出區塊標題"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_section(title: str):
    """印出小節標題"""
    print(f"\n--- {title} ---")


def test_github_api():
    """執行所有 GitHub API 測試"""

    # 確認 token 存在
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("ERROR: GITHUB_TOKEN not set in .env")
        return False

    print(f"GITHUB_TOKEN loaded (length: {len(token)})")
    print("-" * 60)

    # 初始化客戶端
    try:
        client = GitHubClient(token)
        print("GitHubClient initialized successfully")
    except GitHubClientError as e:
        print(f"GitHubClient initialization failed: {e}")
        return False

    results = []

    # 測試 a) get_repo_statistics - Pyroxyl/test-repo
    print_section('a) get_repo_statistics("Pyroxyl", "test-repo")')
    try:
        stats = client.get_repo_statistics("Pyroxyl", "test-repo")
        print(f"   Stars:       {stats['stars']}")
        print(f"   Forks:       {stats['forks']}")
        print(f"   Open Issues: {stats['open_issues']}")
        print(f"   Watchers:    {stats['watchers']}")
        results.append(True)
    except GitHubClientError as e:
        print(f"   ERROR: {e}")
        results.append(False)

    # 測試 b) get_recent_commits - Pyroxyl/test-repo
    print_section('b) get_recent_commits("Pyroxyl", "test-repo", limit=3)')
    try:
        commits = client.get_recent_commits("Pyroxyl", "test-repo", limit=3)
        for i, commit in enumerate(commits, 1):
            sha_short = commit['sha'][:7]
            message = commit['message'].split('\n')[0][:50]
            author = commit['author']
            print(f"   {i}. [{sha_short}] {message}")
            print(f"      Author: {author}")
        results.append(True)
    except GitHubClientError as e:
        print(f"   ERROR: {e}")
        results.append(False)

    # 測試 c) get_contributors_stats - anthropics/anthropic-sdk-python
    print_section('c) get_contributors_stats("anthropics", "anthropic-sdk-python", top_n=3)')
    try:
        contributors = client.get_contributors_stats("anthropics", "anthropic-sdk-python", top_n=3)
        for i, contrib in enumerate(contributors, 1):
            print(f"   {i}. {contrib['login']}: {contrib['contributions']} contributions")
        results.append(True)
    except GitHubClientError as e:
        print(f"   ERROR: {e}")
        results.append(False)

    # 測試 d) get_languages - anthropics/anthropic-sdk-python
    print_section('d) get_languages("anthropics", "anthropic-sdk-python")')
    try:
        languages = client.get_languages("anthropics", "anthropic-sdk-python")
        if not languages:
            print("   (No languages detected)")
        else:
            for lang, percentage in sorted(languages.items(), key=lambda x: -x[1]):
                bar = "#" * int(percentage / 5)
                print(f"   {lang:15} {percentage:5.1f}% {bar}")
        results.append(True)
    except GitHubClientError as e:
        print(f"   ERROR: {e}")
        results.append(False)

    return all(results)


if __name__ == "__main__":
    print_header("GitHub API Real Functionality Test")

    success = test_github_api()

    print_header("Test Results")

    if success:
        print("\n  All GitHub API tests passed!")
        print("\n  Phase 1 complete!")
        print("\n  Ready for Phase 2: Dockerization")
    else:
        print("\n  Some tests failed. Please check the errors above.")

    print("\n" + "=" * 60)

    sys.exit(0 if success else 1)
