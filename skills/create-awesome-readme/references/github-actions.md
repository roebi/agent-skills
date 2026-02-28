# GitHub Actions Workflow Reference

Two workflow variants for automating the awesome README generation
in `roebi/awesome-agent-skills`.

---

## Variant A — aider-chat + aider-skills (roebi/aider-skills)

Uses `aider-chat` as the agent with `aider-skills` to inject the
`create-awesome-readme` skill into aider's context.

`aider-skills` (https://pypi.org/project/aider-skills/) is the bridge package
that generates the `<available_skills>` XML from any Agent Skills directory
and feeds it to aider via a temp file and the `--read` flag — requiring
zero changes to aider's internals.

**File:** `.github/workflows/update-readme-aider.yml`

```yaml
name: Update Awesome README (aider-chat)

on:
  schedule:
    - cron: '0 6 * * 1'   # Every Monday 06:00 UTC
  workflow_dispatch:
    inputs:
      tag:
        description: 'GitHub topic tag to search'
        default: 'agent-skills'
      max_repos:
        description: 'Maximum repositories to process'
        default: '200'
      min_stars:
        description: 'Minimum star count filter'
        default: '0'

jobs:
  update:
    runs-on: ubuntu-latest
    permissions:
      contents: write

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

      - name: Run the three pipeline scripts directly
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          uv run _skills/skills/create-awesome-readme/scripts/fetch-topic-repos.py \
            --tag "${{ inputs.tag || 'agent-skills' }}" \
            --max ${{ inputs.max_repos || '200' }} \
            --min-stars ${{ inputs.min_stars || '0' }} \
            --output /tmp/repos.json

          uv run _skills/skills/create-awesome-readme/scripts/analyze-repos.py \
            --repos /tmp/repos.json \
            --output /tmp/labeled.json

          uv run _skills/skills/create-awesome-readme/scripts/generate-readme.py \
            --labeled /tmp/labeled.json \
            --tag "${{ inputs.tag || 'agent-skills' }}" \
            --output README.md

      - name: Use aider-skills to inject skill context into aider
        # aider-skills tmpfile writes the <available_skills> XML to a temp file
        # and prints its path — aider then reads it via --read at startup.
        # This is the correct integration pattern per roebi/aider-skills docs.
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          SKILL_CONTEXT=$(aider-skills tmpfile _skills/skills/)

          aider \
            --model claude-sonnet-4-5 \
            --read "$SKILL_CONTEXT" \
            --read /tmp/labeled.json \
            README.md \
            --message "You have the create-awesome-readme skill available in context.
              Review the generated README.md against the skill instructions.
              Fix any formatting issues, ensure awesome-list conventions are followed,
              and improve any descriptions that are unclear.
              Do not change the data — only improve presentation." \
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

**Required secrets:**

| Secret | Source |
|--------|--------|
| `ANTHROPIC_API_KEY` | Your Anthropic account — used by aider-chat |
| `GITHUB_TOKEN` | Auto-provided by GitHub Actions — used by fetch script |

### How aider-skills injects the skill

```bash
SKILL_CONTEXT=$(aider-skills tmpfile _skills/skills/create-awesome-readme)
aider --read "$SKILL_CONTEXT" ...
```

`aider-skills tmpfile` does three things:
1. Discovers the skill in the given directory
2. Generates `<available_skills>` XML per the agentskills.io spec
3. Writes it to a temp file and prints the path to stdout

That path is captured into `$SKILL_CONTEXT` and passed to aider via
`--read`, so aider loads the full skill metadata and instructions as
read-only context at startup — with zero changes to aider internals.

Full command reference for `aider-skills`:

| Command | Use |
|---------|-----|
| `aider-skills to-prompt DIR...` | Print XML to stdout — pipe into `/run` inside aider |
| `aider-skills to-conventions DIR...` | Print markdown block — append to `CONVENTIONS.md` |
| `aider-skills tmpfile DIR...` | Write XML to temp file, print path — use with `--read` |
| `aider-skills list DIR...` | Human-readable list of discovered skills |
| `aider-skills validate DIR` | Validate a single skill directory |

---

## Variant B — Claude Code Action (anthropics/claude-code-action)

Uses Anthropic's official GitHub Action running Claude Code as the agent.

**File:** `.github/workflows/update-readme-claude.yml`

```yaml
name: Update Awesome README (Claude Code)

on:
  schedule:
    - cron: '0 6 * * 1'   # Every Monday 06:00 UTC
  workflow_dispatch:
    inputs:
      tag:
        description: 'GitHub topic tag to search'
        default: 'agent-skills'
      max_repos:
        description: 'Maximum repositories to process'
        default: '200'
      min_stars:
        description: 'Minimum star count filter'
        default: '0'

jobs:
  update:
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - uses: actions/checkout@v4

      - name: Checkout agent-skills repo (for the skill)
        uses: actions/checkout@v4
        with:
          repository: roebi/agent-skills
          path: _skills

      - name: Set up Python + uv
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install uv

      - name: Run skill via Claude Code
        uses: anthropics/claude-code-action@beta
        with:
          prompt: |
            Read the skill at _skills/skills/create-awesome-readme/SKILL.md
            and execute the full workflow with TAG=${{ inputs.tag || 'agent-skills' }},
            MAX=${{ inputs.max_repos || '200' }}, MIN_STARS=${{ inputs.min_stars || '0' }}.
            Commit and push the resulting README.md with message:
            "chore: update awesome list [$(date +%Y-%m-%d)]"
          allowed_tools: "Bash,Read,Write"
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Required secrets:**

| Secret | Source |
|--------|--------|
| `ANTHROPIC_API_KEY` | Your Anthropic account |
| `GITHUB_TOKEN` | Auto-provided by GitHub Actions |

---

## Choosing between variants

| | Variant A (aider-skills) | Variant B (Claude Code) |
|---|---|---|
| Agent | aider-chat | Claude Code (Anthropic action) |
| Skill injection | `aider-skills tmpfile` + `--read` | Native (reads SKILL.md directly) |
| Script execution | Scripts run in bash, aider reviews output | Agent runs autonomously |
| Predictability | Deterministic pipeline + AI review pass | Agent decides what to run |
| Cost | Lower (scripts direct + one aider pass) | Higher (full agentic loop) |
| Skill validator | `aider-skills validate` | Built-in |

Variant A is more predictable for CI — the three scripts always run in
order, and aider only does a final review/formatting pass via the injected
skill context. Variant B gives the agent full autonomy but is less deterministic.

---

## Rate limiting

GitHub Search API limits:
- **60 req/hour** unauthenticated
- **5000 req/hour** with `GITHUB_TOKEN`

Always pass `GITHUB_TOKEN` to the fetch script via the environment.
