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
| `MAX_REPOS` | No | Maximum repos to process (default: 40) |
| `MIN_STARS` | No | Filter out repos below this star count — applied server-side at GitHub API (default: 3) |

Environment variable `GITHUB_TOKEN` is optional but strongly recommended
to avoid rate limiting (60 req/hr unauthenticated vs 5000/hr authenticated).

## Labels applied to each repository

Each repository gets one **primary category label** and zero or more
**signal labels** based on content analysis.

### Primary category labels

| Label | Meaning |
|-------|---------|
| `skill` | Repository contains one valid Agent Skill (has `SKILL.md`) |
| `skill-collection` | Repository contains multiple skills |
| `skill-integration` | Integrates or serves Agent Skills (CLI, MCP server, extension) |
| `skill-manager` | Package manager, installer, or registry for Agent Skills |
| `awesome-list` | Another curated awesome list about skills or agents |
| `framework` | Agent framework that supports skills |
| `example` | Demo, tutorial, or example project |
| `other` | Tagged `agent-skills` but content is unrelated to the spec |

### Signal labels

Two confidence levels are used for security signals to avoid false accusations.
See `references/security-labels.md` for full detection patterns.

| Label | Icon | Meaning |
|-------|------|---------|
| `spec-compliant` | ✅ | SKILL.md passes agentskills.io validation |
| `spec-errors` | ❌ | SKILL.md found but fails validation |
| `multi-agent` | 🌐 | Works across multiple agent products |
| `has-scripts` | 📜 | Contains a `scripts/` directory |
| `has-references` | 📚 | Contains a `references/` directory |
| `misleading` | ⚠️ | Topic tag used for SEO — content unrelated to Agent Skills |
| `env-stealer` | 🚨 | **Confirmed:** scripts exfiltrate environment variables |
| `env-stealer?` | ⚠️ | **Unverified:** suspicious pattern, needs human review |
| `rm-rf` | 💥 | **Confirmed:** destructive `rm -rf` on root, home, or wildcard |
| `rm-rf?` | ⚠️ | **Unverified:** `rm -rf $VAR` — may be safe, needs human review |
| `archived` | 🗄️ | Repository is archived |
| `stale` | 💤 | No commits in 6+ months |
| `no-license` | 🔓 | No LICENSE file found |

## Workflow

### Step 1: Fetch repositories for the topic

```bash
uv run scripts/fetch-topic-repos.py \
  --tag "$TAG" \
  --max "$MAX_REPOS" \
  --min-stars "$MIN_STARS" \
  --output repos.json
```

Calls the GitHub Search API with `q=topic:TAG stars:>=MIN_STARS` — star
filtering happens server-side so no wasted API calls. Results are sorted
by stars descending.

### Step 2: Analyze and label each repository

```bash
uv run scripts/analyze-repos.py \
  --repos repos.json \
  --output labeled.json
```

For each repository this script:
1. Fetches the repository tree (GitHub API `/repos/{owner}/{repo}/git/trees/HEAD?recursive=1`)
2. Checks for the presence of `SKILL.md` files (anywhere in tree)
3. Downloads and validates each `SKILL.md` frontmatter against agentskills.io spec
4. Checks for `scripts/`, `references/` directories
5. Scans scripts for security signals using two-level detection (confirmed / unverified)
6. Determines primary category label and signal labels
7. Writes enriched repo objects to `labeled.json`

### Step 3: Generate the README

```bash
uv run scripts/generate-readme.py \
  --labeled labeled.json \
  --tag "$TAG" \
  --output "$OUTPUT"
```

Assembles the README in awesome-list format with sections, label legend,
and summary table. See `references/readme-format.md` for the output structure.

## Running in GitHub Actions

The skill is designed to run as a scheduled GitHub Actions workflow using
`aider-chat` + `aider-skills` for the review pass. The skill is injected
into aider via `aider-skills tmpfile` which generates `<available_skills>`
XML and passes it to aider via `--read`.

The working workflow for `roebi/awesome-agent-skills` is:

```yaml
name: Update Awesome README (aider-chat)

on:
  schedule:
    - cron: '0 15 * * 5'   # Every Friday 15:00 UTC
    - cron: '0 6 * * 1'    # Every Monday 06:00 UTC
  workflow_dispatch:
    inputs:
      tag:
        description: 'GitHub topic tag to search'
        default: 'agent-skills'
      max_repos:
        description: 'Maximum repositories to process'
        default: '40'
      min_stars:
        description: 'Minimum star count filter'
        default: '3'

jobs:
  update:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      models: read

    steps:
      - name: Checkout awesome-agent-skills repo
        uses: actions/checkout@v4

      - name: Checkout agent-skills repo (for the skill)
        uses: actions/checkout@v4
        with:
          repository: roebi/agent-skills
          path: _skills

      - name: Set up Python + uv
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install tools
        run: |
          pip install uv
          pip install aider-chat
          pip install aider-skills

      - name: Validate skill before running
        run: |
          aider-skills validate _skills/skills/create-awesome-readme

      - name: Run the three pipeline scripts
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          uv run _skills/skills/create-awesome-readme/scripts/fetch-topic-repos.py \
            --tag "${{ inputs.tag || 'agent-skills' }}" \
            --max ${{ inputs.max_repos || '40' }} \
            --min-stars ${{ inputs.min_stars || '3' }} \
            --output /tmp/repos.json

          uv run _skills/skills/create-awesome-readme/scripts/analyze-repos.py \
            --repos /tmp/repos.json \
            --output /tmp/labeled.json

          uv run _skills/skills/create-awesome-readme/scripts/generate-readme.py \
            --labeled /tmp/labeled.json \
            --tag "${{ inputs.tag || 'agent-skills' }}" \
            --output README.md

      - name: Use aider-skills to inject skill context into aider
        # aider-skills tmpfile generates <available_skills> XML and returns path.
        # aider reads it via --read as read-only context at startup.
        # GitHub Models (gpt-4o) used via GITHUB_TOKEN — no external secret needed.
        # permissions: models: read must be set on the job for GITHUB_TOKEN to work.
        env:
          OPENAI_API_BASE: https://models.inference.ai.azure.com
          OPENAI_API_KEY: ${{ secrets.GITHUB_TOKEN }}
        run: |
          SKILL_CONTEXT=$(aider-skills tmpfile _skills/skills)

          MSG='You have the create-awesome-readme skill loaded in context.
              Read the skill instructions from the XML context file first.
              Then look at each repository entry in README.md that has an empty
              description or a description that is clearly just the repo name
              repeated. For those entries only, write a short one-line description
              based on the repository name, its labels, and its category section.
              Follow the entry line format defined in the skill.
              Do not change any other lines, labels, stars, or structure.'

          aider \
            --model openai/gpt-4o \
            --weak-model openai/gpt-4o \
            --read "$SKILL_CONTEXT" \
            README.md \
            --message "$MSG" \
            --yes \
            --no-auto-commits

      - name: Commit and push README
        run: |
          git config user.name  "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add README.md
          git diff --staged --quiet || \
            git commit -m "chore: update awesome list [$(date +%Y-%m-%d)]"
          git push
```

**Required secrets: none.**
Both `GITHUB_TOKEN` (fetch scripts + aider model via GitHub Models) are
auto-provided by GitHub Actions. `permissions: models: read` must be
explicitly declared on the job for GitHub Models access to work.

### Key lessons learned during development

- `aider-skills tmpfile` takes the **parent** directory containing skill
  subdirectories (`_skills/skills`), not the skill directory itself
  (`_skills/skills/create-awesome-readme`). The `validate` command is the
  opposite — it takes the skill directory directly.
- `--message` strings containing double quotes must use a `MSG=` variable
  with single-quote assignment to avoid shell parsing errors.
- `gpt-4o-mini` on GitHub Models has an 8000 token hard limit. Use `gpt-4o`
  which has 128k context. Do not pass `--read /tmp/labeled.json` to aider —
  the README already contains the derived data and labeled.json is large.
- `permissions: models: read` is required for `GITHUB_TOKEN` to access
  `https://models.inference.ai.azure.com`. Without it the request fails
  with "The `models` permission is required".

## Reference files

- `references/readme-format.md` — exact awesome-list README structure and sections
- `references/security-labels.md` — full detection patterns for security signal labels
- `references/github-actions.md` — full workflow templates (Variant A: aider-skills, Variant B: Claude Code)
