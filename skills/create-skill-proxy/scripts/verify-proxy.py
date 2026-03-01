#!/usr/bin/env python3
# /// script
# dependencies = [
#   "requests>=2.32,<3",
#   "PyYAML>=6,<7",
# ]
# requires-python = ">=3.11"
# ///
"""
Re-verify a 'Skill Proxy' against its pinned remote content.

Fetches the pinned URL and checks the SHA-256 matches the proxy metadata.
Also checks if a newer commit exists on the tracked branch.

DISCLAIMER: The creator of the 'Skill Proxy' is not liable for any damages
arising from the use of this 'Skill Proxy'. The risk and responsibility lies
exclusively with the user who uses this 'Skill Proxy'. If the 'Skill Proxy'
user is an agent, then the user who is responsible for that agent bears
the responsibility.

Usage:
  scripts/verify-proxy.py --proxy ./skills/skill-container-proxy

Exit codes:
  0  Checksum matches — proxy is intact
  1  Usage error
  2  Network error
  4  Checksum mismatch — remote content has changed
"""

import argparse
import hashlib
import os
import re
import sys
from pathlib import Path

try:
    import requests
    import yaml
except ImportError:
    print("Error: Run with: uv run scripts/verify-proxy.py", file=sys.stderr)
    sys.exit(2)


def load_proxy_metadata(proxy_dir: Path) -> dict:
    skill_md = proxy_dir / "SKILL.md"
    if not skill_md.exists():
        print(f"Error: no SKILL.md found in {proxy_dir}", file=sys.stderr)
        sys.exit(1)
    content = skill_md.read_text(encoding="utf-8")
    if not content.startswith("---"):
        print("Error: SKILL.md has no frontmatter", file=sys.stderr)
        sys.exit(1)
    end = content.find("---", 3)
    fm = yaml.safe_load(content[3:end]) or {}
    return fm.get("metadata", {})


def fetch_pinned(url: str) -> str:
    try:
        resp = requests.get(url, timeout=20)
    except requests.RequestException as e:
        print(f"Error fetching pinned URL: {e}", file=sys.stderr)
        sys.exit(2)
    if resp.status_code != 200:
        print(f"Error: HTTP {resp.status_code} fetching {url}", file=sys.stderr)
        sys.exit(2)
    return resp.text


def get_latest_commit(owner: str, repo: str, branch: str) -> str | None:
    token = os.environ.get("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        resp = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}/commits/{branch}",
            headers=headers, timeout=20
        )
        if resp.status_code == 200:
            return resp.json()["sha"]
    except Exception:
        pass
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--proxy", required=True,
                        help="Path to the proxy skill directory")
    args = parser.parse_args()

    proxy_dir = Path(args.proxy)
    print(f"Verifying 'Skill Proxy': {proxy_dir}", file=sys.stderr)
    print(f"⚠ Reminder: risk and responsibility for use lies with the user.",
          file=sys.stderr)

    meta = load_proxy_metadata(proxy_dir)

    pinned_url    = meta.get("proxy-raw-url")
    expected_sha  = meta.get("proxy-sha256")
    pinned_commit = meta.get("proxy-commit")
    branch        = meta.get("proxy-branch", "main")
    source_url    = meta.get("proxy-source", "")
    created_by    = meta.get("proxy-created-by", "unknown")
    created_at    = meta.get("proxy-created-at", "unknown")

    if not pinned_url or not expected_sha:
        print("Error: proxy metadata missing proxy-raw-url or proxy-sha256", file=sys.stderr)
        sys.exit(1)

    print(f"  Created by    : {created_by}", file=sys.stderr)
    print(f"  Created at    : {created_at}", file=sys.stderr)
    print(f"  Pinned commit : {pinned_commit[:12] if pinned_commit else 'unknown'}",
          file=sys.stderr)
    print(f"  Expected SHA  : {expected_sha[:16]}...", file=sys.stderr)

    # Fetch pinned content
    print("Fetching pinned URL...", file=sys.stderr)
    content = fetch_pinned(pinned_url)

    # Verify checksum
    actual_sha = hashlib.sha256(content.encode("utf-8")).hexdigest()
    if actual_sha == expected_sha:
        print("  ✓ Checksum matches — 'Skill Proxy' is intact", file=sys.stderr)
    else:
        print("  ✗ CHECKSUM MISMATCH", file=sys.stderr)
        print(f"    Expected : {expected_sha}", file=sys.stderr)
        print(f"    Actual   : {actual_sha}", file=sys.stderr)
        print("", file=sys.stderr)
        print("The remote content at the pinned commit has changed.", file=sys.stderr)
        print("This should not happen — GitHub commit content is immutable.", file=sys.stderr)
        print("Something may be wrong with the 'Skill Proxy' metadata.", file=sys.stderr)
        sys.exit(4)

    # Check if upstream has newer commits
    m = re.search(r'github\.com/([^/]+)/([^/]+)', source_url)
    if m:
        owner, repo = m.group(1), m.group(2)
        print(f"Checking for upstream updates on branch '{branch}'...", file=sys.stderr)
        latest = get_latest_commit(owner, repo, branch)
        if latest and latest != pinned_commit:
            print(f"  ℹ Upstream has a newer commit: {latest[:12]}", file=sys.stderr)
            print("    Review upstream changes, then run update-proxy.py to update the pin.",
                  file=sys.stderr)
        elif latest:
            print(f"  ✓ 'Skill Proxy' is at HEAD of branch '{branch}'", file=sys.stderr)

    print(f"\n✓ 'Skill Proxy' is intact: {proxy_dir.name}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
