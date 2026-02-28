#!/usr/bin/env python3
# /// script
# dependencies = [
#   "requests>=2.32,<3",
# ]
# requires-python = ">=3.11"
# ///
"""
Fetch GitHub repositories for a given topic tag.

Calls the GitHub Search API to collect repo metadata and writes
results to a JSON file for downstream analysis.

Usage:
  scripts/fetch-topic-repos.py --tag agent-skills --output repos.json
  scripts/fetch-topic-repos.py --tag agent-skills --max 500 --min-stars 5

Exit codes:
  0  Success
  1  Usage/argument error
  2  Network or API error
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

try:
    import requests
except ImportError:
    print("Error: requests is required. Run: uv run scripts/fetch-topic-repos.py", file=sys.stderr)
    sys.exit(2)


def fetch_repos(tag: str, max_repos: int, min_stars: int, token: str | None) -> list[dict]:
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    else:
        print("Warning: GITHUB_TOKEN not set. Rate limited to 60 requests/hour.", file=sys.stderr)

    repos = []
    page = 1
    per_page = 100

    while len(repos) < max_repos:
        url = "https://api.github.com/search/repositories"
        params = {
            "q": f"topic:{tag}",
            "sort": "stars",
            "order": "desc",
            "per_page": min(per_page, max_repos - len(repos)),
            "page": page,
        }

        print(f"Fetching page {page} ({len(repos)} repos so far)...", file=sys.stderr)

        try:
            resp = requests.get(url, headers=headers, params=params, timeout=30)
        except requests.RequestException as e:
            print(f"Error: network request failed: {e}", file=sys.stderr)
            sys.exit(2)

        if resp.status_code == 403:
            reset = resp.headers.get("X-RateLimit-Reset", "unknown")
            print(f"Error: rate limited. Resets at {reset}. Set GITHUB_TOKEN to increase limit.", file=sys.stderr)
            sys.exit(2)

        if resp.status_code != 200:
            print(f"Error: GitHub API returned {resp.status_code}: {resp.text}", file=sys.stderr)
            sys.exit(2)

        data = resp.json()
        items = data.get("items", [])

        if not items:
            print(f"No more results at page {page}.", file=sys.stderr)
            break

        for item in items:
            if item.get("stargazers_count", 0) < min_stars:
                continue
            repos.append({
                "id": item["id"],
                "full_name": item["full_name"],
                "owner": item["owner"]["login"],
                "name": item["name"],
                "description": item.get("description") or "",
                "html_url": item["html_url"],
                "stars": item["stargazers_count"],
                "forks": item["forks_count"],
                "language": item.get("language"),
                "topics": item.get("topics", []),
                "archived": item.get("archived", False),
                "updated_at": item.get("updated_at"),
                "created_at": item.get("created_at"),
                "license": (item.get("license") or {}).get("spdx_id"),
                "default_branch": item.get("default_branch", "main"),
            })

        total_count = data.get("total_count", 0)
        print(f"Total matching repos: {total_count}. Fetched so far: {len(repos)}.", file=sys.stderr)

        if len(items) < per_page or len(repos) >= max_repos:
            break

        page += 1
        # Respect secondary rate limits
        time.sleep(1)

    return repos


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--tag", required=True,
                        help="GitHub topic tag to search (e.g. agent-skills)")
    parser.add_argument("--max", type=int, default=200,
                        dest="max_repos",
                        help="Maximum number of repos to fetch (default: 200)")
    parser.add_argument("--min-stars", type=int, default=0,
                        help="Minimum star count to include (default: 0)")
    parser.add_argument("--output", default="repos.json",
                        help="Output JSON file path (default: repos.json)")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    repos = fetch_repos(args.tag, args.max_repos, args.min_stars, token)

    output = {
        "tag": args.tag,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "total": len(repos),
        "repos": repos,
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(repos)} repos to {args.output}", file=sys.stderr)
    print(json.dumps({"output": args.output, "count": len(repos)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
