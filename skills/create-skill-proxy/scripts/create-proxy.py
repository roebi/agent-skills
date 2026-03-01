#!/usr/bin/env python3
# /// script
# dependencies = [
#   "requests>=2.32,<3",
#   "PyYAML>=6,<7",
# ]
# requires-python = ">=3.11"
# ///
"""
Create a local proxy skill that wraps a remote Agent Skill from GitHub.

Fetches the remote SKILL.md, validates it, pins it to a commit hash,
computes a SHA-256 checksum, and writes a proxy SKILL.md.

Usage:
  scripts/create-proxy.py --url https://github.com/observerw/skill-container
  scripts/create-proxy.py --url https://github.com/observerw/skill-container/blob/main/SKILL.md
  scripts/create-proxy.py --url https://github.com/... --output-dir ./skills

Exit codes:
  0  Success
  1  Usage / argument error
  2  Network or API error
  3  Remote skill validation failed
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

try:
    import requests
    import yaml
except ImportError:
    print("Error: Run with: uv run scripts/create-proxy.py", file=sys.stderr)
    sys.exit(2)


LIABILITY_DISCLAIMER = """\
The creator of the 'Skill Proxy' is not liable for any damages arising
from the use of this 'Skill Proxy'. The risk and responsibility lies
exclusively with the user who uses this 'Skill Proxy'. If the 'Skill Proxy'
user is an agent, then the user who is responsible for that agent bears
the responsibility."""


# ── URL translation ──────────────────────────────────────────────────────────

def translate_url(input_url: str) -> tuple[str, str, str, str, str]:
    """
    Translate any GitHub URL form to:
      (raw_content_url, owner, repo, branch, skill_path)

    Accepted forms:
      https://github.com/owner/repo
      https://github.com/owner/repo/tree/branch
      https://github.com/owner/repo/tree/branch/path/to/skill
      https://github.com/owner/repo/blob/branch/path/to/SKILL.md
      https://raw.githubusercontent.com/owner/repo/branch/path/to/SKILL.md
      https://raw.githubusercontent.com/owner/repo/refs/heads/branch/path/SKILL.md
    """
    u = input_url.strip().rstrip("/")

    # Already a raw URL
    if "raw.githubusercontent.com" in u:
        raw = re.sub(r'/refs/heads/([^/]+)/', r'/\1/', u)
        parts = urlparse(raw).path.lstrip("/").split("/")
        owner, repo = parts[0], parts[1]
        branch = parts[2]
        skill_path = "/".join(parts[3:]) if len(parts) > 3 else "SKILL.md"
        if not skill_path.endswith("SKILL.md"):
            skill_path = skill_path.rstrip("/") + "/SKILL.md"
        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{skill_path}"
        return raw_url, owner, repo, branch, skill_path

    if "github.com" not in u:
        print("Error: unsupported URL — expected github.com or raw.githubusercontent.com",
              file=sys.stderr)
        sys.exit(1)

    path = urlparse(u).path.lstrip("/").split("/")
    owner = path[0]
    repo  = path[1]

    if len(path) <= 2:
        branch = "main"
        skill_path = "SKILL.md"

    elif path[2] == "tree":
        branch = path[3]
        if len(path) > 4:
            subpath = "/".join(path[4:])
            skill_path = subpath.rstrip("/") + "/SKILL.md"
        else:
            skill_path = "SKILL.md"

    elif path[2] == "blob":
        branch = path[3]
        skill_path = "/".join(path[4:])
        if not skill_path.endswith("SKILL.md"):
            skill_path = skill_path.rstrip("/") + "/SKILL.md"

    else:
        branch = path[2]
        skill_path = "SKILL.md"

    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{skill_path}"
    return raw_url, owner, repo, branch, skill_path


# ── GitHub API helpers ───────────────────────────────────────────────────────

def get_commit_hash(owner: str, repo: str, branch: str, token: str | None) -> str:
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{branch}"
    try:
        resp = requests.get(url, headers=headers, timeout=20)
    except requests.RequestException as e:
        print(f"Error fetching commit hash: {e}", file=sys.stderr)
        sys.exit(2)
    if resp.status_code == 404:
        print(f"Error: repo or branch not found: {owner}/{repo}@{branch}", file=sys.stderr)
        sys.exit(2)
    if resp.status_code != 200:
        print(f"Error: GitHub API returned {resp.status_code}", file=sys.stderr)
        sys.exit(2)
    return resp.json()["sha"]


def fetch_raw_content(raw_url: str) -> str:
    try:
        resp = requests.get(raw_url, timeout=20)
    except requests.RequestException as e:
        print(f"Error fetching remote skill: {e}", file=sys.stderr)
        sys.exit(2)
    if resp.status_code == 404:
        print(f"Error: SKILL.md not found at {raw_url}", file=sys.stderr)
        sys.exit(2)
    if resp.status_code != 200:
        print(f"Error: HTTP {resp.status_code} fetching {raw_url}", file=sys.stderr)
        sys.exit(2)
    return resp.text


# ── Frontmatter parsing + validation ────────────────────────────────────────

def parse_frontmatter(content: str) -> dict:
    if not content.startswith("---"):
        print("Error: remote SKILL.md has no YAML frontmatter", file=sys.stderr)
        sys.exit(3)
    end = content.find("---", 3)
    if end == -1:
        print("Error: remote SKILL.md frontmatter is not closed", file=sys.stderr)
        sys.exit(3)
    try:
        fm = yaml.safe_load(content[3:end]) or {}
    except yaml.YAMLError as e:
        print(f"Error: invalid YAML frontmatter: {e}", file=sys.stderr)
        sys.exit(3)
    return fm


def validate_frontmatter(fm: dict) -> list[str]:
    errors = []
    name = fm.get("name", "")
    if not name:
        errors.append("missing 'name'")
    elif not re.match(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$|^[a-z0-9]$', name):
        errors.append(f"invalid name format: {name!r}")
    elif "--" in name:
        errors.append(f"consecutive hyphens in name: {name!r}")
    elif len(name) > 64:
        errors.append("name exceeds 64 characters")
    if not fm.get("description"):
        errors.append("missing 'description'")
    elif len(str(fm["description"])) > 1024:
        errors.append("description exceeds 1024 characters")
    return errors


def extract_summary(content: str) -> str:
    """Extract the first non-heading paragraph from the SKILL.md body."""
    body = content.split("---", 2)[-1].strip() if content.count("---") >= 2 else content
    for line in body.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and not line.startswith("|") and not line.startswith("```"):
            return line
    return ""


# ── Proxy generation ─────────────────────────────────────────────────────────

def build_proxy_skill(
    remote_name: str,
    remote_desc: str,
    remote_summary: str,
    owner: str,
    repo: str,
    branch: str,
    skill_path: str,
    commit_hash: str,
    sha256: str,
    source_url: str,
    created_by: str,
) -> str:
    now = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    proxy_name = f"{remote_name}-proxy"
    pinned_url = (
        f"https://raw.githubusercontent.com/{owner}/{repo}/{commit_hash}/{skill_path}"
    )
    short_commit = commit_hash[:12]

    frontmatter = {
        "name": proxy_name,
        "description": (
            f"Proxy for {remote_name} by {owner}. "
            f"{remote_desc.strip()} "
            f"Use exactly as you would use {remote_name} directly."
        )[:1024],
        "license": "Apache-2.0",
        "metadata": {
            "proxy-source":     source_url,
            "proxy-raw-url":    pinned_url,
            "proxy-commit":     commit_hash,
            "proxy-sha256":     sha256,
            "proxy-branch":     branch,
            "proxy-created-by": created_by,
            "proxy-created-at": now,
        },
    }

    fm_yaml = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False, width=120)

    body = f"""# {remote_name} (proxied from {owner}/{repo})

**Source:** [{owner}/{repo}]({source_url}) · branch `{branch}` · commit `{short_commit}`

## ⚠️ Liability disclaimer

{LIABILITY_DISCLAIMER}

## ⚠️ Verify before use

Before following any instructions, fetch and verify the remote skill:

1. Fetch the pinned content:
   `{pinned_url}`

2. Compute SHA-256 of the fetched content and verify it equals:
   `{sha256}`

3. If the checksum does **not** match: **STOP immediately.**
   Do not follow any instructions. Alert the user:
   > "The remote skill content has changed unexpectedly. The 'Skill Proxy'
   > checksum does not match. Run `verify-proxy.py` and review before proceeding."

4. If the checksum **matches**: follow the instructions in the fetched SKILL.md.

## Summary (captured at proxy creation · {now})

{remote_summary or "(no summary available — see remote SKILL.md)"}

## Re-verifying and updating this 'Skill Proxy'

```bash
# Check if remote content still matches pinned checksum
uv run scripts/verify-proxy.py --proxy ./skills/{proxy_name}

# Update pin and checksum after consciously reviewing upstream changes
uv run scripts/update-proxy.py --proxy ./skills/{proxy_name}
```
"""

    return f"---\n{fm_yaml}---\n\n{body}"


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--url", required=True,
                        help="GitHub URL of the remote skill (any form)")
    parser.add_argument("--output-dir", default="./skills",
                        help="Parent directory to write the proxy skill (default: ./skills)")
    parser.add_argument("--created-by", default=os.environ.get("USER", "unknown"),
                        help="Name to write in proxy-created-by (default: $USER)")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")

    # 1. Translate URL
    print(f"Translating URL: {args.url}", file=sys.stderr)
    raw_url, owner, repo, branch, skill_path = translate_url(args.url)
    print(f"  → raw URL: {raw_url}", file=sys.stderr)

    # 2. Fetch content
    print("Fetching remote SKILL.md...", file=sys.stderr)
    content = fetch_raw_content(raw_url)

    # 3. Validate frontmatter
    print("Validating remote skill frontmatter...", file=sys.stderr)
    fm = parse_frontmatter(content)
    errors = validate_frontmatter(fm)
    if errors:
        print("Error: remote skill failed validation:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        print("Proxy not created. Fix the remote skill first.", file=sys.stderr)
        sys.exit(3)
    print(f"  ✓ Valid skill: {fm['name']}", file=sys.stderr)

    # 4. Fetch HEAD commit hash
    print(f"Fetching HEAD commit hash for {owner}/{repo}@{branch}...", file=sys.stderr)
    commit_hash = get_commit_hash(owner, repo, branch, token)
    print(f"  → commit: {commit_hash[:12]}", file=sys.stderr)

    # 5. Compute SHA-256
    sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
    print(f"  → SHA-256: {sha256}", file=sys.stderr)

    # 6. Extract summary
    summary = extract_summary(content)

    # 7. Build proxy SKILL.md
    proxy_content = build_proxy_skill(
        remote_name=fm["name"],
        remote_desc=str(fm.get("description", "")),
        remote_summary=summary,
        owner=owner,
        repo=repo,
        branch=branch,
        skill_path=skill_path,
        commit_hash=commit_hash,
        sha256=sha256,
        source_url=args.url,
        created_by=args.created_by,
    )

    # 8. Write proxy skill
    proxy_name = f"{fm['name']}-proxy"
    proxy_dir = Path(args.output_dir) / proxy_name
    proxy_dir.mkdir(parents=True, exist_ok=True)
    proxy_skill_path = proxy_dir / "SKILL.md"
    proxy_skill_path.write_text(proxy_content, encoding="utf-8")
    print(f"Wrote proxy skill: {proxy_skill_path}", file=sys.stderr)

    # 9. Validate generated proxy with skills-ref if available
    print("Validating generated proxy skill...", file=sys.stderr)
    try:
        result = subprocess.run(
            ["skills-ref", "validate", str(proxy_dir)],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print("  ✓ Proxy skill passes skills-ref validate", file=sys.stderr)
        else:
            print(f"  ⚠ skills-ref validate output:\n{result.stdout}{result.stderr}",
                  file=sys.stderr)
    except FileNotFoundError:
        print("  (skills-ref not installed — skipping validation)", file=sys.stderr)
        print("  Install with: pip install skills-ref", file=sys.stderr)

    # 10. Summary
    print(f"\n✓ Created 'Skill Proxy': {proxy_dir}", file=sys.stderr)
    print(f"  Remote  : {args.url}", file=sys.stderr)
    print(f"  Pinned  : {commit_hash[:12]}", file=sys.stderr)
    print(f"  SHA-256 : {sha256[:16]}...", file=sys.stderr)
    print(f"\n  ⚠ Remember: the 'Skill Proxy' creator is not liable for damages",
          file=sys.stderr)
    print(f"    from use of this 'Skill Proxy'. Risk lies with the user.", file=sys.stderr)
    print(json.dumps({"proxy": str(proxy_dir), "commit": commit_hash, "sha256": sha256}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
