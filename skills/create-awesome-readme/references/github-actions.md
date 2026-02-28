# GitHub Actions Workflow Reference

Complete workflow template for automating the awesome README generation
in `roebi/awesome-agent-skills`.

## Workflow: `.github/workflows/update-readme.yml`

```yaml
name: Update Awesome README

on:
  # Run every Monday at 06:00 UTC
  schedule:
    - cron: '0 6 * * 1'

  # Allow manual runs with optional tag override
  workflow_dispatch:
    inputs:
      tag:
        description: 'GitHub topic tag to search'
        required: false
        default: 'agent-skills'
      max_repos:
        description: 'Maximum repositories to process'
        required: false
        default: '200'
      min_stars:
        description: 'Minimum star count filter'
        required: false
        default: '0'

jobs:
  update-readme:
    runs-on: ubuntu-latest
    permissions:
      contents: write   # needed to commit README.md back

    steps:
      - name: Checkout awesome-agent-skills repo
        uses: actions/checkout@v4

      - name: Checkout agent-skills repo (for the skill)
        uses: actions/checkout@v4
        with:
          repository: roebi/agent-skills
          path: _skills

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install uv
        run: pip install uv

      - name: Run create-awesome-readme skill via Claude Code
        uses: anthropics/claude-code-action@beta
        with:
          prompt: |
            You are running the `create-awesome-readme` Agent Skill.
            Read the skill instructions at: _skills/skills/create-awesome-readme/SKILL.md

            Then execute the full workflow:

            1. Run the fetch script:
               uv run _skills/skills/create-awesome-readme/scripts/fetch-topic-repos.py \
                 --tag "${{ inputs.tag || 'agent-skills' }}" \
                 --max ${{ inputs.max_repos || '200' }} \
                 --min-stars ${{ inputs.min_stars || '0' }} \
                 --output /tmp/repos.json

            2. Run the analyze script:
               uv run _skills/skills/create-awesome-readme/scripts/analyze-repos.py \
                 --repos /tmp/repos.json \
                 --output /tmp/labeled.json

            3. Run the generate script:
               uv run _skills/skills/create-awesome-readme/scripts/generate-readme.py \
                 --labeled /tmp/labeled.json \
                 --tag "${{ inputs.tag || 'agent-skills' }}" \
                 --output README.md

            4. Verify README.md looks correct and complete.
            5. Stage, commit, and push README.md with message:
               "chore: update awesome list [$(date +%Y-%m-%d)]"
          allowed_tools: "Bash,Read,Write"
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Required secrets

Set these in `roebi/awesome-agent-skills` → Settings → Secrets → Actions:

| Secret | Description |
|--------|-------------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key for Claude Code |
| `GITHUB_TOKEN` | Auto-provided by GitHub Actions — no setup needed |

## Manual trigger

Go to: `https://github.com/roebi/awesome-agent-skills/actions`
→ Select "Update Awesome README"
→ Click "Run workflow"
→ Optionally override `tag`, `max_repos`, `min_stars`

## Commit strategy

The workflow commits directly to the default branch. For a review-based
approach, change the last step to open a Pull Request instead:

```yaml
      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v6
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          commit-message: "chore: update awesome list"
          title: "Update Awesome README - ${{ github.run_id }}"
          branch: "auto/update-readme-${{ github.run_id }}"
          base: main
```

## Rate limiting

The GitHub Search API allows:
- **60 requests/hour** unauthenticated
- **5000 requests/hour** authenticated (GITHUB_TOKEN)

For 200 repos × ~5 API calls each = ~1000 calls. Always use GITHUB_TOKEN.

## Cost estimate

Processing 200 repos with Claude Code typically uses:
- ~100K–300K tokens depending on analysis depth
- Approximately $0.30–$1.00 per run at current Sonnet pricing
