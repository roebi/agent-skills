#!/usr/bin/env python3
# /// script
# dependencies = []
# requires-python = ">=3.11"
# ///
"""
Generate an awesome-list README.md from labeled repository data.

Usage:
  scripts/generate-readme.py --labeled labeled.json --tag agent-skills
  scripts/generate-readme.py --labeled labeled.json --tag agent-skills --output README.md

Exit codes:
  0  Success
  1  Usage/argument error
"""

import argparse
import json
import sys
from datetime import datetime, timezone


CATEGORY_ORDER = [
    "skill-collection",
    "skill",
    "skill-manager",
    "skill-integration",
    "awesome-list",
    "framework",
    "example",
    "other",
]

CATEGORY_HEADINGS = {
    "skill-collection":  "## 📦 Skill Collections",
    "skill":             "## 🎯 Individual Skills",
    "skill-manager":     "## 🛠️ Skill Managers & Registries",
    "skill-integration": "## 🔌 Integrations & Tooling",
    "awesome-list":      "## 📋 Other Awesome Lists",
    "framework":         "## 🏗️ Frameworks & SDKs",
    "example":           "## 💡 Examples & Demos",
    "other":             "## 🔍 Other",
}

CATEGORY_DESCRIPTIONS = {
    "skill-collection":  "Repositories containing multiple Agent Skills.",
    "skill":             "Repositories containing a single Agent Skill.",
    "skill-manager":     "Tools to discover, install, and manage Agent Skills.",
    "skill-integration": "Products and tools that integrate or serve Agent Skills.",
    "awesome-list":      "Other curated lists about Agent Skills or related topics.",
    "framework":         "Agent frameworks and SDKs with Agent Skills support.",
    "example":           "Demos, tutorials, and sample projects.",
    "other":             "Repositories tagged `agent-skills` with other content.",
}

SIGNAL_ICONS = {
    "spec-compliant": "✅",
    "multi-agent":    "🌐",
    "has-scripts":    "📜",
    "has-references": "📚",
    "misleading":     "⚠️",
    "env-stealer":    "🚨",
    "rm-rf":          "💥",
    "archived":       "🗄️",
    "stale":          "💤",
    "no-license":     "🔓",
    "spec-errors":    "❌",
}

ADVISORY_SIGNALS = {"misleading", "env-stealer", "rm-rf", "archived", "stale", "no-license", "spec-errors", "error"}


def format_signals(signals: list[str]) -> str:
    parts = []
    for s in sorted(signals):
        icon = SIGNAL_ICONS.get(s, "")
        if icon:
            parts.append(f"`{s}` {icon}")
        else:
            parts.append(f"`{s}`")
    return " ".join(parts)


def format_repo_entry(repo: dict) -> str:
    name = repo["full_name"]
    url = repo.get("html_url", f"https://github.com/{name}")
    desc = repo.get("description") or ""
    stars = repo.get("stars", 0)
    lang = repo.get("language") or ""
    signals = repo.get("signal_labels", [])

    # Build the line
    line = f"- **[{name}]({url})** — {desc}"

    # Stars badge
    line += f" ⭐ {stars}"

    # Language badge if present
    if lang:
        line += f" `{lang}`"

    # Signal labels
    advisory = [s for s in signals if s in ADVISORY_SIGNALS]
    positive = [s for s in signals if s not in ADVISORY_SIGNALS]

    if positive:
        line += " " + format_signals(positive)
    if advisory:
        line += " " + format_signals(advisory)

    return line


def generate_readme(data: dict, tag: str) -> str:
    repos = data["repos"]
    analyzed_at = data.get("analyzed_at", "")
    total = data.get("total", len(repos))

    # Group by primary label, exclude repos with advisory-only labels from main sections
    by_category: dict[str, list] = {cat: [] for cat in CATEGORY_ORDER}
    for repo in repos:
        label = repo.get("primary_label", "other")
        if label in by_category:
            by_category[label].append(repo)
        else:
            by_category["other"].append(repo)

    # Sort each category by stars descending
    for cat in by_category:
        by_category[cat].sort(key=lambda r: r.get("stars", 0), reverse=True)

    # Count stats
    skill_count = len(by_category["skill"]) + len(by_category["skill-collection"])
    integration_count = len(by_category["skill-integration"]) + len(by_category["skill-manager"])
    misleading_count = sum(
        1 for r in repos if "misleading" in r.get("signal_labels", [])
    )
    security_count = sum(
        1 for r in repos if any(s in r.get("signal_labels", []) for s in ("env-stealer", "rm-rf"))
    )

    lines = []

    # Header
    lines += [
        f"# Awesome Agent Skills · `{tag}`",
        "",
        f"> A curated and automatically labeled list of GitHub repositories tagged "
        f"[`{tag}`](https://github.com/topics/{tag}).",
        "> Powered by the [agentskills.io](https://agentskills.io) open specification.",
        "",
        "[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)",
        "",
        f"*Auto-generated · {total} repositories analyzed · "
        f"Last updated: `{analyzed_at[:10] if analyzed_at else 'unknown'}`*",
        "",
    ]

    # Stats summary
    lines += [
        "## Summary",
        "",
        f"| Category | Count |",
        f"|----------|-------|",
        f"| Skills & collections | {skill_count} |",
        f"| Integrations & managers | {integration_count} |",
        f"| Misleading / off-topic | {misleading_count} |",
        f"| Security signals | {security_count} |",
        f"| Total | {total} |",
        "",
    ]

    # Label legend
    lines += [
        "## Label Legend",
        "",
        "| Label | Meaning |",
        "|-------|---------|",
        "| `spec-compliant` ✅ | SKILL.md passes agentskills.io validation |",
        "| `multi-agent` 🌐 | Works across multiple agent products |",
        "| `has-scripts` 📜 | Contains a `scripts/` directory |",
        "| `has-references` 📚 | Contains a `references/` directory |",
        "| `misleading` ⚠️ | Topic tag used for SEO — not actually an Agent Skill |",
        "| `env-stealer` 🚨 | Scripts or actions exfiltrate environment variables |",
        "| `rm-rf` 💥 | Destructive `rm -rf` without safeguards |",
        "| `archived` 🗄️ | Repository is archived |",
        "| `stale` 💤 | No commits in 6+ months |",
        "| `no-license` 🔓 | No LICENSE file found |",
        "",
    ]

    # Sections
    for cat in CATEGORY_ORDER:
        repos_in_cat = by_category[cat]
        if not repos_in_cat:
            continue

        lines += [
            CATEGORY_HEADINGS[cat],
            "",
            f"*{CATEGORY_DESCRIPTIONS[cat]}*",
            "",
        ]

        for repo in repos_in_cat:
            lines.append(format_repo_entry(repo))

        lines.append("")

    # Footer
    lines += [
        "---",
        "",
        "## Contributing",
        "",
        f"This list is auto-generated from the GitHub topic "
        f"[`{tag}`](https://github.com/topics/{tag}).",
        "To add your repository, add the `agent-skills` topic to it on GitHub.",
        "",
        "To suggest a label correction or report a false positive, open an issue.",
        "",
        "## License",
        "",
        "[CC0 1.0](LICENSE)",
    ]

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--labeled", required=True,
                        help="Input labeled.json from analyze-repos.py")
    parser.add_argument("--tag", required=True,
                        help="GitHub topic tag (used in headings and links)")
    parser.add_argument("--output", default="README.md",
                        help="Output README.md path (default: README.md)")
    args = parser.parse_args()

    with open(args.labeled, encoding="utf-8") as f:
        data = json.load(f)

    readme = generate_readme(data, args.tag)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(readme)

    print(f"Wrote README to {args.output} ({len(readme)} chars)", file=sys.stderr)
    print(json.dumps({"output": args.output, "chars": len(readme)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
