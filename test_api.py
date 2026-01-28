#!/usr/bin/env python3
"""Test REST API endpoints."""

import sys
import requests

BASE_URL = "http://localhost:8080"


def print_header(title: str):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_section(title: str):
    print(f"\n--- {title} ---")


def test_endpoint(method: str, path: str, expected_status: int = 200) -> dict | None:
    """Call an endpoint and return the JSON response."""
    url = f"{BASE_URL}{path}"
    print(f"   {method} {path}")
    try:
        resp = requests.get(url, timeout=30)
        print(f"   Status: {resp.status_code}")
        if resp.status_code != expected_status:
            print(f"   ERROR: Expected {expected_status}, got {resp.status_code}")
            print(f"   Body: {resp.text[:200]}")
            return None
        data = resp.json()
        return data
    except requests.ConnectionError:
        print(f"   ERROR: Cannot connect to {BASE_URL}")
        print("   Is the API gateway running? (make run-api)")
        return None
    except Exception as e:
        print(f"   ERROR: {e}")
        return None


def main():
    print_header("GitHub Analytics REST API Test")
    results = []

    # 1. Health check
    print_section("1) GET /health")
    data = test_endpoint("GET", "/health")
    if data:
        print(f"   Response: {data}")
        results.append(data.get("status") == "ok")
    else:
        results.append(False)

    # 2. Repo stats
    print_section("2) GET /api/v1/repo/Pyroxyl/test-repo/stats")
    data = test_endpoint("GET", "/api/v1/repo/Pyroxyl/test-repo/stats")
    if data:
        print(f"   Stars: {data.get('stars')}, Forks: {data.get('forks')}")
        print(f"   Issues: {data.get('open_issues')}, Watchers: {data.get('watchers')}")
        results.append(True)
    else:
        results.append(False)

    # 3. Recent commits
    print_section("3) GET /api/v1/repo/Pyroxyl/test-repo/commits?limit=3")
    data = test_endpoint("GET", "/api/v1/repo/Pyroxyl/test-repo/commits?limit=3")
    if data:
        commits = data.get("commits", [])
        for i, c in enumerate(commits, 1):
            print(f"   {i}. [{c['sha'][:7]}] {c['message'][:50]}")
        results.append(True)
    else:
        results.append(False)

    # 4. Contributors
    print_section("4) GET /api/v1/repo/anthropics/anthropic-sdk-python/contributors?top_n=3")
    data = test_endpoint("GET", "/api/v1/repo/anthropics/anthropic-sdk-python/contributors?top_n=3")
    if data:
        for i, c in enumerate(data.get("contributors", []), 1):
            print(f"   {i}. {c['login']}: {c['contributions']} contributions")
        results.append(True)
    else:
        results.append(False)

    # 5. Languages
    print_section("5) GET /api/v1/repo/anthropics/anthropic-sdk-python/languages")
    data = test_endpoint("GET", "/api/v1/repo/anthropics/anthropic-sdk-python/languages")
    if data:
        for lang, pct in sorted(data.get("languages", {}).items(), key=lambda x: -x[1]):
            print(f"   {lang:15} {pct:5.1f}%")
        results.append(True)
    else:
        results.append(False)

    # 6. API docs
    print_section("6) GET /docs (OpenAPI documentation)")
    data = test_endpoint("GET", "/docs")
    if data is not None or True:  # /docs returns HTML, not JSON
        resp = requests.get(f"{BASE_URL}/docs", timeout=10)
        ok = resp.status_code == 200
        print(f"   Status: {resp.status_code}")
        print(f"   Content-Type: {resp.headers.get('content-type', 'N/A')}")
        results.append(ok)

    # Summary
    print_header("Test Results")
    passed = sum(results)
    total = len(results)

    if all(results):
        print(f"\n  All {total} API tests passed!")
        print("\n  Phase 3 complete!")
    else:
        print(f"\n  {passed}/{total} tests passed.")
        print("  Some tests failed. Check errors above.")

    print("\n" + "=" * 60)
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
