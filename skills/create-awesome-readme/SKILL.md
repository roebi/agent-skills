---
name: create-awesome-readme
description: >
  Generates a curated awesome-list README.md by discovering GitHub repositories
  under a given topic tag, analyzing each repository's content, and labeling
  them by category and quality signals. Use when a user wants to create or
  update an awesome list, curate a collection of GitHub repos by topic,
  generate a categorized README from a GitHub topic search, or automate
  awesome-list maintenance. Trigger phrases: "create awesome list",
  "update awesome readme", "curate repos by topic", "generate README from
  GitHub topic", "label repos from topic tag".
compatibility: Requires Python 3.11+, uv or pip. GitHub token recommended for API rate limits.
metadata:
  author: roebi
  repo: https://github.com/roebi/agent-skills
---

# Create Awesome README

Discovers GitHub repositories for a given topic tag, analyzes and labels each
repository, and generates a curated `README.md` in the style of
[awesome lists](https://github.com/sindresorhus/awesome).

## Inputs

| Parameter | Required | Description |
|-----------|----------|-------------|
| `TAG` | Yes | GitHub topic tag, e.g. `agent-skills` |
| `OUTPUT` | No | Output file path (default: `README.md`) |
| `MAX_REPOS` | No | Maximum repos to process (default: 200) |
| `MIN_STARS` | No | Filter out repos below this star count (default: 0) |

Environment variable `GITHUB_TOKEN` is optional but strongly recommended
to avoid rate limiting (60 req/hr unauthenticated vs 5000/hr authenticated).

## Labels applied to each repository

Each repository gets one **primary category label** and zero or more
**signal labels** based on content analysis.

### Primary category labels

| Label | Meaning |
|-------|---------|
| `skill` | Repository contains one or more valid Agent Skills (has `SKILL.md`) |
| `skill-collection` | Repository contains multiple skills |
| `skill-integration` | Integrates or serves Agent Skills (CLI, MCP server, extension) |
| `skill-manager` | Package manager, installer, or registry for Agent Skills |
| `awesome-list` | Another curated awesome list about skills or agents |
| `framework` | Agent framework that supports skills |
| `example` | Demo, tutorial, or example project |
| `other` | Tagged `agent-skills` but content is unrelated to the spec |

### Signal labels (advisory)

| Label | Meaning |
|-------|---------|
| `spec-compliant` | SKILL.md passes `skills-ref validate` |
| `has-scripts` | Contains a `scripts/` directory |
| `has-references` | Contains a `references/` directory |
| `multi-agent` | Works across multiple agent products |
| `archived` | Repository is archived |
| `misleading` | Topic tag used for SEO — content unrelated to Agent Skills spec |
| `env-stealer` | Scripts or actions read and exfiltrate environment variables |
| `rm-rf` | Scripts contain destructive `rm -rf` without safeguards |
| `no-license` | No LICENSE file found |
| `stale` | No commits in 6+ months |

## Workflow

### Step 1: Fetch repositories for the topic

```bash
uv run scripts/fetch-topic-repos.py \
  --tag "$TAG" \
  --max "$MAX_REPOS" \
  --output repos.json
```

This calls `https://github.com/topics/<TAG>` (HTML scraping) and the GitHub
Search API (`https://api.github.com/search/repositories?topic=<TAG>`) to
collect repo metadata: name, description, stars, forks, language, updated_at,
topics, archived status.

### Step 2: Analyze and label each repository

```bash
uv run scripts/analyze-repos.py \
  --repos repos.json \
  --output labeled.json
```

For each repository this script:
1. Fetches the repository tree (GitHub API `/repos/{owner}/{repo}/git/trees/HEAD?recursive=1`)
2. Checks for the presence of `SKILL.md` files (anywhere in tree)
3. Downloads and validates each `SKILL.md` frontmatter
4. Checks for `scripts/`, `references/`, `assets/` directories
5. Scans scripts for security signals (`rm -rf`, `env`, `curl | bash` without pinning)
6. Determines primary category label and signal labels
7. Writes enriched repo objects to `labeled.json`

### Step 3: Generate the README

```bash
uv run scripts/generate-readme.py \
  --labeled labeled.json \
  --tag "$TAG" \
  --output "$OUTPUT"
```

This assembles the README in awesome-list format. See `references/readme-format.md`
for the exact output structure.

## Security label detection rules

These rules are applied in `analyze-repos.py`. See `references/security-labels.md`
for full patterns.

**`env-stealer`** — any of:
- Script sends `env` or `printenv` output to an external URL via curl/wget
- Script exports secrets to a remote endpoint
- GitHub Actions workflow exfiltrates `${{ secrets.* }}` to untrusted destinations

**`rm-rf`** — any of:
- `rm -rf /` or `rm -rf /*` anywhere in scripts or workflows
- `rm -rf` on a variable path without `--dry-run` guard or explicit user confirmation

**`misleading`** — heuristic: repository has `agent-skills` topic but:
- No `SKILL.md` found anywhere in tree, AND
- Description contains no mention of skills, agents, or Claude Code, AND
- Primary language is not Python/Shell/TypeScript (common skill languages)

## Running in GitHub Actions

The skill is designed to run as a GitHub Actions workflow using an AI agent.
See `references/github-actions.md` for the complete workflow template.

Quick example for `roebi/awesome-agent-skills/.github/workflows/update-readme.yml`:

```yaml
name: Update Awesome README
on:
  schedule:
    - cron: '0 6 * * 1'   # Every Monday at 06:00 UTC
  workflow_dispatch:
    inputs:
      tag:
        description: 'GitHub topic tag to search'
        default: 'agent-skills'

jobs:
  update:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - uses: anthropics/claude-code-action@beta
        with:
          prompt: |
            Use the create-awesome-readme skill located at
            skills/create-awesome-readme/SKILL.md.
            Run it with TAG=${{ inputs.tag || 'agent-skills' }}.
            Commit and push the resulting README.md.
          skills: skills/
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Reference files

- `references/readme-format.md` — exact awesome-list README structure and sections
- `references/security-labels.md` — full detection patterns for security signal labels
- `references/github-actions.md` — complete GitHub Actions workflow template
