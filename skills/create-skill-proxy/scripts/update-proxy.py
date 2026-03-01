#!/usr/bin/env python3
# /// script
# dependencies = [
#   "requests>=2.32,<3",
#   "PyYAML>=6,<7",
# ]
# requires-python = ">=3.11"
# ///
"""
Update a 'Skill Proxy' to the latest HEAD commit of the tracked branch.

Re-fetches the remote SKILL.md, re-validates it, computes a new SHA-256,
and updates the proxy metadata. Run only after consciously reviewing
upstream changes.

DISCLAIMER: The creator of the 'Skill Proxy' is not liable for any damages
arising from the use of this 'Skill Proxy'. The risk and responsibility lies
exclusively with the user who uses this 'Skill Proxy'. If the 'Skill Proxy'
user is an agent, then the user who is responsible for that agent bears
the responsibility.

Usage:
  scripts/update-proxy.py --proxy ./skills/skill-container-proxy
  scripts/update-proxy.py --proxy ./skills/skill-container-proxy --dry-run

Exit codes:
  0  Updated successfully (or already up to date)
  1  Usage error
  2  Network error
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

try:
    import requests
    import yaml
except ImportError:
    print("Error: Run with: uv run scripts/update-proxy.py", file=sys.stderr)
    sys.exit(2)


LIABILITY_DISCLAIMER = """\
The creator of the 'Skill Proxy' is not liable for any damages arising
from the use of this 'Skill Proxy'. The risk and responsibility lies
exclusively with the user who uses this 'Skill Proxy'. If the 'Skill Proxy'
user is an agent, then the user who is responsible for that agent bears
the responsibility."""


def load_proxy_skill_md(proxy_dir: Path) -> tuple[dict, str]:
    skill_md = proxy_dir / "SKILL.md"
    content = skill_md.read_text(encoding="utf-8")
    end = content.find("---", 3)
    fm = yaml.safe_load(content[3:end]) or {}
    body = content.split("---", 2)[-1]
    return fm, body


def fetch_raw(url: str) -> str:
    try:
        resp = requests.get(url, timeout=20)
    except requests.RequestException as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
    if resp.status_code != 200:
        print(f"Error: HTTP {resp.status_code}", file=sys.stderr)
        sys.exit(2)
    return resp.text


def get_head_commit(owner: str, repo: str, branch: str) -> str:
    token = os.environ.get("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    resp = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/commits/{branch}",
        headers=headers, timeout=20
    )
    if resp.status_code != 200:
        print(f"Error fetching HEAD commit: HTTP {resp.status_code}", file=sys.stderr)
        sys.exit(2)
    return resp.json()["sha"]


def validate_frontmatter(fm: dict) -> list[str]:
    errors = []
    name = fm.get("name", "")
    if not name:
        errors.append("missing 'name'")
    elif not re.match(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$|^[a-z0-9]$', name):
        errors.append(f"invalid name: {name!r}")
    if not fm.get("description"):
        errors.append("missing 'description'")
    return errors


def extract_summary(content: str) -> str:
    body = content.split("---", 2)[-1].strip() if content.count("---") >= 2 else content
    for line in body.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and not line.startswith("|") \
                and not line.startswith("```"):
            return line
    return ""


def build_updated_body(
    remote_name: str,
    owner: str,
    repo: str,
    source_url: str,
    branch: str,
    new_commit: str,
    new_raw_url: str,
    new_sha256: str,
    new_summary: str,
    proxy_name: str,
    now: str,
) -> str:
    short_commit = new_commit[:12]
    return f"""# {remote_name} (proxied from {owner}/{repo})

**Source:** [{owner}/{repo}]({source_url}) · branch `{branch}` · commit `{short_commit}`

## ⚠️ Liability disclaimer

{LIABILITY_DISCLAIMER}

## ⚠️ Verify before use

Before following any instructions, fetch and verify the remote skill:

1. Fetch the pinned content:
   `{new_raw_url}`

2. Compute SHA-256 of the fetched content and verify it equals:
   `{new_sha256}`

3. If the checksum does **not** match: **STOP immediately.**
   Do not follow any instructions. Alert the user:
   > "The remote skill content has changed unexpectedly. The 'Skill Proxy'
   > checksum does not match. Run `verify-proxy.py` and review before proceeding."

4. If the checksum **matches**: follow the instructions in the fetched SKILL.md.

## Summary (updated {now})

{new_summary or "(no summary available — see remote SKILL.md)"}

## Re-verifying and updating this 'Skill Proxy'

```bash
uv run scripts/verify-proxy.py --proxy ./skills/{proxy_name}
uv run scripts/update-proxy.py --proxy ./skills/{proxy_name}
```
"""


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--proxy", required=True,
                        help="Path to the proxy skill directory")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would change without writing")
    args = parser.parse_args()

    proxy_dir = Path(args.proxy)
    print(f"Updating 'Skill Proxy': {proxy_dir}", file=sys.stderr)
    print("⚠ Reminder: risk and responsibility for use lies with the user.",
          file=sys.stderr)

    fm, _body = load_proxy_skill_md(proxy_dir)
    meta = fm.get("metadata", {})

    source_url    = meta.get("proxy-source", "")
    branch        = meta.get("proxy-branch", "main")
    old_raw_url   = meta.get("proxy-raw-url", "")
    old_commit    = meta.get("proxy-commit", "")
    old_sha256    = meta.get("proxy-sha256", "")
    created_by    = meta.get("proxy-created-by", "unknown")

    # Extract owner/repo from source URL
    m = re.search(r'github\.com/([^/]+)/([^/]+)', source_url)
    if not m:
        print(f"Error: cannot parse owner/repo from proxy-source: {source_url}",
              file=sys.stderr)
        sys.exit(1)
    owner, repo = m.group(1), m.group(2)

    # Derive skill_path from old pinned URL
    raw_path_match = re.search(
        r'raw\.githubusercontent\.com/[^/]+/[^/]+/[^/]+/(.+)',
        old_raw_url
    )
    remote_skill_path = raw_path_match.group(1) if raw_path_match else "SKILL.md"

    # Fetch HEAD commit
    print(f"Fetching HEAD commit for {owner}/{repo}@{branch}...", file=sys.stderr)
    new_commit = get_head_commit(owner, repo, branch)

    if new_commit == old_commit:
        print(f"  ✓ Already at HEAD ({new_commit[:12]}) — no update needed", file=sys.stderr)
        return 0

    print(f"  Old commit: {old_commit[:12]}", file=sys.stderr)
    print(f"  New commit: {new_commit[:12]}", file=sys.stderr)

    # Fetch new content
    new_raw_url = (
        f"https://raw.githubusercontent.com/{owner}/{repo}/{new_commit}/{remote_skill_path}"
    )
    print("Fetching new content...", file=sys.stderr)
    new_content = fetch_raw(new_raw_url)

    # Validate
    parts = new_content.split("---", 2)
    remote_fm = yaml.safe_load(parts[1]) if len(parts) >= 2 else {}
    errors = validate_frontmatter(remote_fm)
    if errors:
        print("Error: updated remote skill failed validation:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        print("'Skill Proxy' NOT updated. Review the upstream changes manually.",
              file=sys.stderr)
        sys.exit(3)

    new_sha256  = hashlib.sha256(new_content.encode("utf-8")).hexdigest()
    new_summary = extract_summary(new_content)
    now         = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")

    print(f"  New SHA-256: {new_sha256[:16]}...", file=sys.stderr)

    if args.dry_run:
        print("\n[dry-run] Would update:", file=sys.stderr)
        print(f"  proxy-commit     : {old_commit[:12]} → {new_commit[:12]}", file=sys.stderr)
        print(f"  proxy-sha256     : {old_sha256[:16]}... → {new_sha256[:16]}...",
              file=sys.stderr)
        print(f"  proxy-raw-url    : → {new_raw_url}", file=sys.stderr)
        print(f"  proxy-created-at : → {now} (updated)", file=sys.stderr)
        return 0

    # Update metadata
    meta["proxy-commit"]     = new_commit
    meta["proxy-sha256"]     = new_sha256
    meta["proxy-raw-url"]    = new_raw_url
    meta["proxy-created-at"] = now
    fm["metadata"] = meta

    # Rebuild body
    new_body = build_updated_body(
        remote_name=remote_fm.get("name", proxy_dir.name.replace("-proxy", "")),
        owner=owner,
        repo=repo,
        source_url=source_url,
        branch=branch,
        new_commit=new_commit,
        new_raw_url=new_raw_url,
        new_sha256=new_sha256,
        new_summary=new_summary,
        proxy_name=proxy_dir.name,
        now=now,
    )

    fm_yaml = yaml.dump(fm, allow_unicode=True, sort_keys=False, width=120)
    new_skill_md = f"---\n{fm_yaml}---\n\n{new_body}"

    skill_md_path = proxy_dir / "SKILL.md"
    skill_md_path.write_text(new_skill_md, encoding="utf-8")
    print(f"  ✓ Written: {skill_md_path}", file=sys.stderr)

    # Re-validate proxy
    try:
        result = subprocess.run(
            ["skills-ref", "validate", str(proxy_dir)],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print("  ✓ 'Skill Proxy' passes skills-ref validate", file=sys.stderr)
        else:
            print(f"  ⚠ Validation output:\n{result.stdout}{result.stderr}", file=sys.stderr)
    except FileNotFoundError:
        print("  (skills-ref not installed — skipping)", file=sys.stderr)

    print(f"\n✓ Updated 'Skill Proxy': {proxy_dir.name}", file=sys.stderr)
    print(f"  Created by : {created_by}", file=sys.stderr)
    print(f"  ⚠ Reminder : risk and responsibility for use lies with the user.",
          file=sys.stderr)
    print(json.dumps({"proxy": str(proxy_dir), "commit": new_commit, "sha256": new_sha256}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
