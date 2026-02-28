#!/usr/bin/env python3
# /// script
# dependencies = [
#   "requests>=2.32,<3",
#   "PyYAML>=6,<7",
# ]
# requires-python = ">=3.11"
# ///
"""
Analyze and label GitHub repositories for the awesome-list generator.

Fetches each repo's file tree, checks for SKILL.md files, validates
frontmatter, scans for security signals, and assigns category/signal labels.

Security signals use two levels:
  CONFIRMED (💥 / 🚨): pattern is unambiguously dangerous
  UNVERIFIED (⚠️):     pattern matches but may be a false positive — needs human review

Usage:
  scripts/analyze-repos.py --repos repos.json --output labeled.json
  scripts/analyze-repos.py --repos repos.json --output labeled.json --limit 50

Exit codes:
  0  Success
  1  Usage/argument error
  2  Network or API error
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone

try:
    import requests
    import yaml
except ImportError:
    print("Error: Run with: uv run scripts/analyze-repos.py", file=sys.stderr)
    sys.exit(2)


# ── Security signal patterns ────────────────────────────────────────────────
#
# CONFIRMED patterns: unambiguously dangerous, no legitimate use case
# UNVERIFIED patterns: suspicious but common in legitimate scripts too
#
# rm -rf CONFIRMED — only fire on clearly destructive targets:
#   rm -rf /          (root filesystem)
#   rm -rf /*         (root with wildcard)
#   rm -rf ~          (home directory)
#   rm -rf ~/         (home directory with slash)
#   rm -rf *          (wildcard from current dir — dangerous in wrong context)
#
# rm -rf UNVERIFIED — suspicious but needs human review:
#   rm -rf $VAR       (unquoted variable — depends on what $VAR contains)
#   rm -rf ${VAR}     (same with braces)
#
# Explicitly NOT flagged (safe, very common):
#   rm -rf ./dist     (relative path with explicit ./)
#   rm -rf ./tmp
#   rm -rf ./build
#   rm -rf node_modules
#   rm -rf $TMPDIR/specific-subpath  (explicit subpath after variable)

RM_RF_CONFIRMED = [
    # rm -rf / or rm -rf /* (root)
    re.compile(r'rm\s+-[a-zA-Z]*rf[a-zA-Z]*\s+/\*?(?:\s|$)', re.IGNORECASE),
    # rm -rf ~ or rm -rf ~/
    re.compile(r'rm\s+-[a-zA-Z]*rf[a-zA-Z]*\s+~/?(?:\s|$)', re.IGNORECASE),
    # rm -rf * (bare wildcard, not ./*)
    re.compile(r'rm\s+-[a-zA-Z]*rf[a-zA-Z]*\s+\*(?:\s|$)', re.IGNORECASE),
]

RM_RF_UNVERIFIED = [
    # rm -rf $VAR or rm -rf ${VAR} where the variable is at end of line
    # (no further path component after the variable)
    re.compile(r'rm\s+-[a-zA-Z]*rf[a-zA-Z]*\s+\$\{?\w+\}?\s*(?:#.*)?$', re.IGNORECASE | re.MULTILINE),
]

# ENV exfiltration CONFIRMED — clearly piping env to remote
ENV_EXFIL_CONFIRMED = [
    re.compile(r'(env|printenv|set)\s*\|.*curl', re.IGNORECASE),
    re.compile(r'curl[^|]*\$\{?GITHUB_TOKEN[^|]*\|\s*nc\b', re.IGNORECASE),
]

# ENV exfiltration UNVERIFIED — sending a secret via curl (common in CI but worth noting)
ENV_EXFIL_UNVERIFIED = [
    re.compile(r'curl.*\$\{?GITHUB_TOKEN', re.IGNORECASE),
    re.compile(r'curl.*\$\{?secrets\.', re.IGNORECASE),
    re.compile(r'wget.*\$(HOME|USER|PATH)\b', re.IGNORECASE),
]

SKILL_RELEVANT_KEYWORDS = {
    "skill", "agent", "claude", "llm", "ai agent", "coding agent",
    "SKILL.md", "agentskills", "assistant", "copilot",
}

SKILL_LANGUAGES = {"Python", "Shell", "TypeScript", "JavaScript"}


def github_get(url: str, headers: dict, retries: int = 3) -> dict | None:
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=headers, timeout=20)
        except requests.RequestException as e:
            print(f"  Network error ({url}): {e}", file=sys.stderr)
            time.sleep(2 ** attempt)
            continue

        if resp.status_code == 404:
            return None
        if resp.status_code == 403:
            print(f"  Rate limited. Waiting 60s...", file=sys.stderr)
            time.sleep(60)
            continue
        if resp.status_code != 200:
            print(f"  HTTP {resp.status_code} for {url}", file=sys.stderr)
            return None

        return resp.json()
    return None


def get_file_tree(owner: str, name: str, branch: str, headers: dict) -> list[str]:
    url = f"https://api.github.com/repos/{owner}/{name}/git/trees/{branch}?recursive=1"
    data = github_get(url, headers)
    if not data:
        return []
    return [item["path"] for item in data.get("tree", []) if item.get("type") == "blob"]


def get_file_content(owner: str, name: str, path: str, headers: dict) -> str | None:
    import base64
    url = f"https://api.github.com/repos/{owner}/{name}/contents/{path}"
    data = github_get(url, headers)
    if not data or data.get("encoding") != "base64":
        return None
    try:
        return base64.b64decode(data["content"]).decode("utf-8", errors="replace")
    except Exception:
        return None


def parse_skill_md_frontmatter(content: str) -> dict | None:
    if not content.startswith("---"):
        return None
    end = content.find("---", 3)
    if end == -1:
        return None
    try:
        return yaml.safe_load(content[3:end]) or {}
    except yaml.YAMLError:
        return None


def validate_frontmatter(fm: dict) -> list[str]:
    """Return list of validation errors."""
    errors = []
    name = fm.get("name", "")
    if not name:
        errors.append("missing name")
    elif not re.match(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$|^[a-z0-9]$', name):
        errors.append(f"invalid name: {name!r}")
    elif "--" in name:
        errors.append(f"consecutive hyphens in name: {name!r}")
    elif len(name) > 64:
        errors.append("name exceeds 64 chars")

    desc = fm.get("description", "")
    if not desc:
        errors.append("missing description")
    elif len(str(desc)) > 1024:
        errors.append("description exceeds 1024 chars")

    return errors


def scan_for_security_signals(content: str) -> list[str]:
    """
    Returns list of signal label strings.
    Confirmed dangerous patterns → 'rm-rf' or 'env-stealer'
    Unverified/suspicious patterns → 'rm-rf?' or 'env-stealer?'
    A confirmed signal supersedes the unverified one for the same type.
    """
    signals = []

    # Check rm-rf confirmed first
    rm_confirmed = any(p.search(content) for p in RM_RF_CONFIRMED)
    if rm_confirmed:
        signals.append("rm-rf")
    else:
        rm_unverified = any(p.search(content) for p in RM_RF_UNVERIFIED)
        if rm_unverified:
            signals.append("rm-rf?")

    # Check env-stealer confirmed first
    env_confirmed = any(p.search(content) for p in ENV_EXFIL_CONFIRMED)
    if env_confirmed:
        signals.append("env-stealer")
    else:
        env_unverified = any(p.search(content) for p in ENV_EXFIL_UNVERIFIED)
        if env_unverified:
            signals.append("env-stealer?")

    return signals


def is_misleading(repo: dict, has_skill_md: bool) -> bool:
    if has_skill_md:
        return False
    desc = (repo.get("description") or "").lower()
    name = repo.get("name", "").lower()
    topics = [t.lower() for t in repo.get("topics", [])]
    lang = repo.get("language")

    desc_relevant = any(kw.lower() in desc for kw in SKILL_RELEVANT_KEYWORDS)
    topics_relevant = any(
        kw.lower() in " ".join(topics)
        for kw in {"skill", "agent", "claude", "llm"}
    )
    lang_relevant = lang in SKILL_LANGUAGES

    return not desc_relevant and not topics_relevant and not lang_relevant


def classify_repo(repo: dict, tree: list[str], skill_mds: list[str], security_signals: list[str]) -> dict:
    has_skill_md = len(skill_mds) > 0
    has_scripts = any(p.startswith("scripts/") or "/scripts/" in p for p in tree)
    has_references = any(p.startswith("references/") or "/references/" in p for p in tree)
    has_license = any(p.lower() in ("license", "license.txt", "license.md") for p in tree)
    archived = repo.get("archived", False)

    # Staleness: no commits in 6 months
    stale = False
    updated_at = repo.get("updated_at")
    if updated_at:
        try:
            updated = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
            age_days = (datetime.now(timezone.utc) - updated).days
            stale = age_days > 180
        except ValueError:
            pass

    # Primary category
    if has_skill_md:
        if len(skill_mds) > 1:
            primary = "skill-collection"
        else:
            primary = "skill"
    else:
        desc = (repo.get("description") or "").lower()
        name = repo.get("name", "").lower()
        all_text = desc + " " + name + " " + " ".join(repo.get("topics", []))
        if any(kw in all_text for kw in ["marketplace", "package manager", "registry", "paks", "skillport"]):
            primary = "skill-manager"
        elif any(kw in all_text for kw in ["integrate", "integration", "mcp", "extension", "cli", "server"]):
            primary = "skill-integration"
        elif any(kw in all_text for kw in ["awesome", "curated", "collection", "list"]):
            primary = "awesome-list"
        elif any(kw in all_text for kw in ["framework", "sdk", "library"]):
            primary = "framework"
        elif any(kw in all_text for kw in ["example", "demo", "tutorial", "sample"]):
            primary = "example"
        elif is_misleading(repo, has_skill_md):
            primary = "other"
            security_signals = list(set(security_signals + ["misleading"]))
        else:
            primary = "other"

    # Signal labels
    signals = list(security_signals)
    if has_skill_md:
        signals.append("spec-compliant")  # downgraded later if validation fails
    if has_scripts:
        signals.append("has-scripts")
    if has_references:
        signals.append("has-references")
    if archived:
        signals.append("archived")
    if stale:
        signals.append("stale")
    if not has_license:
        signals.append("no-license")

    topics = repo.get("topics", [])
    if any(t in topics for t in ["multi-agent", "claude-code", "copilot", "gemini-cli", "codex"]):
        signals.append("multi-agent")

    return {
        "primary_label": primary,
        "signal_labels": sorted(set(signals)),
        "has_skill_md": has_skill_md,
        "skill_md_paths": skill_mds,
    }


def analyze_repo(repo: dict, headers: dict) -> dict:
    owner = repo["owner"]
    name = repo["name"]
    branch = repo.get("default_branch", "main")

    print(f"  Analyzing {owner}/{name}...", file=sys.stderr)

    tree = get_file_tree(owner, name, branch, headers)
    time.sleep(0.5)  # gentle rate limiting

    skill_md_paths = [p for p in tree if p.endswith("SKILL.md")]
    security_signals = []
    validation_errors = []

    # Analyze SKILL.md files
    for skill_path in skill_md_paths[:5]:
        content = get_file_content(owner, name, skill_path, headers)
        if content:
            fm = parse_skill_md_frontmatter(content)
            if fm:
                errs = validate_frontmatter(fm)
                validation_errors.extend(errs)
        time.sleep(0.3)

    # Scan scripts for security signals
    script_paths = [p for p in tree if
                    (p.startswith("scripts/") or "/scripts/" in p) and
                    (p.endswith(".py") or p.endswith(".sh") or p.endswith(".bash"))]
    for script_path in script_paths[:10]:
        content = get_file_content(owner, name, script_path, headers)
        if content:
            sigs = scan_for_security_signals(content)
            security_signals.extend(sigs)
        time.sleep(0.2)

    classification = classify_repo(repo, tree, skill_md_paths, list(set(security_signals)))

    # Downgrade spec-compliant if validation errors found
    if validation_errors and "spec-compliant" in classification["signal_labels"]:
        classification["signal_labels"].remove("spec-compliant")
        classification["signal_labels"].append("spec-errors")

    return {
        **repo,
        **classification,
        "validation_errors": validation_errors,
        "file_count": len(tree),
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--repos", required=True,
                        help="Input repos.json from fetch-topic-repos.py")
    parser.add_argument("--output", default="labeled.json",
                        help="Output labeled JSON file (default: labeled.json)")
    parser.add_argument("--limit", type=int, default=0,
                        help="Process only first N repos (0 = all, default: 0)")
    args = parser.parse_args()

    with open(args.repos, encoding="utf-8") as f:
        data = json.load(f)

    repos = data["repos"]
    if args.limit > 0:
        repos = repos[:args.limit]

    token = os.environ.get("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    else:
        print("Warning: GITHUB_TOKEN not set. May hit rate limits.", file=sys.stderr)

    labeled = []
    for i, repo in enumerate(repos, 1):
        print(f"[{i}/{len(repos)}] {repo['full_name']}", file=sys.stderr)
        try:
            result = analyze_repo(repo, headers)
            labeled.append(result)
        except Exception as e:
            print(f"  Error analyzing {repo['full_name']}: {e}", file=sys.stderr)
            labeled.append({**repo, "primary_label": "other", "signal_labels": ["error"], "error": str(e)})

    output = {
        "tag": data.get("tag"),
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
        "total": len(labeled),
        "repos": labeled,
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nWrote {len(labeled)} labeled repos to {args.output}", file=sys.stderr)
    print(json.dumps({"output": args.output, "count": len(labeled)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
