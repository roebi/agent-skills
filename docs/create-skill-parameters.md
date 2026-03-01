# create-skill pipeline — parameters & file placement

## Parameters

| # | Parameter | Type | Description | Example |
|---|-----------|------|-------------|---------|
| 1 | `TICKET_NUMBER` / `issue_number` | String | Ticket or issue number — used in branch name. Jenkins: full ticket string. GitHub Actions: issue number digits only. | `TESTAUFG-1234` / `5` |
| 2 | `SKILL_NAME` / `skill_name` | String | New skill name. Lowercase, hyphens only, no consecutive hyphens. Agentskills.io spec compliant. | `validate-xml` |
| 3 | `SKILL_DOES` / `skill_does` | Text | What the skill does. One or two sentences. Combined with SKILL_WHEN into the description field. | `Validates XML files against an XSD schema and reports errors with line numbers.` |
| 4 | `SKILL_WHEN` / `skill_when` | Text | When to use it — trigger situations for the agent. Combined with SKILL_DOES into the description field. | `Use when working with XML files, validating configuration, or checking document structure against a schema.` |
| 5 | `SKILL_KEYWORDS` / `skill_keywords` | String | Keywords helping agents identify relevant tasks. Comma separated. | `xml, validate, schema, xsd, lint` |
| 6 | `CREATOR_SKILL_URL` / `creator_skill_url` | String | URL of the creator skill. Any GitHub URL form accepted. | `https://github.com/roebi/agent-skills/blob/main/skills/create-agent-skill/SKILL.md` |
| 7 | `TARGET_REPO` | String | Target git repo URL. Jenkins only — GitHub Actions uses current repo. | `https://github.com/roebi/tide-skills.git` |
| 8 | `MODEL` / `model` | String | Model for aider. On tide-skills auto-resolved via LiteLLM. | Jenkins: `claude-sonnet-4-6` · GitHub Actions: `openai/gpt-4o` |

## Branch naming

| Repo | Pattern | Example |
|------|---------|---------|
| tide-skills (Jenkins) | `feature/<TICKET_NUMBER>-<skill-name>` | `feature/TESTAUFG-1234-validate-xml` |
| agent-skills (GitHub Actions) | `feature/issue-<n>-<skill-name>` | `feature/issue-5-validate-xml` |

## Jenkins credentials required

Configure these in Jenkins → Manage Jenkins → Credentials:

| Credential ID | Type | Value |
|--------------|------|-------|
| `LITELLM_API_KEY` | Secret text | LiteLLM API key |
| `LITELLM_API_BASE` | Secret text | LiteLLM base URL, e.g. `https://litellm.example.com` |
| `GITHUB_TOKEN_JENKINS` | Secret text | GitHub token with `repo` + `pull_request` scope |

## File placement

### roebi/tide-skills (root level)

```
tide-skills/
├── Dockerfile                    ← shared container image
├── create-skill-entrypoint.sh   ← shared entrypoint script
├── Jenkinsfile.groovy            ← Jenkins pipeline definition
└── skills/                       ← existing skills directory
```

### roebi/agent-skills (root + workflow)

```
agent-skills/
├── Dockerfile                    ← shared container image (identical)
├── create-skill-entrypoint.sh   ← shared entrypoint script (identical)
├── .github/
│   └── workflows/
│       └── create-skill.yml     ← GitHub Actions workflow
└── skills/                       ← existing skills directory
```

## Model resolution (tide-skills / LiteLLM)

The entrypoint queries `${OPENAI_API_BASE}/v1/models` at runtime and matches
the `MODEL` parameter value against registered model IDs. Matching tries:

1. Exact match: `claude-sonnet-4-6` == `claude-sonnet-4-6`
2. Suffix with `/`: `anthropic/claude-sonnet-4-6` ends with `/claude-sonnet-4-6`
3. Suffix with `-`: less common prefix patterns

Falls back to using `MODEL` as-is if the endpoint is unreachable or no match found.

## What the pipeline does

1. Validate parameters (fail fast before any git or container work)
2. Build container image from `Dockerfile`
3. Run container — inside the container:
   - Resolve model via LiteLLM (tide-skills only)
   - Clone target repo into container
   - Create and checkout feature branch
   - Fetch creator skill from GitHub URL
   - Build aider-skills XML context from local `./skills/`
   - Run aider with combined SKILL_DOES + SKILL_WHEN + SKILL_KEYWORDS as message
   - Validate generated skill with `aider-skills validate` (fallback: `skills-ref`)
   - Commit generated skill
   - Push feature branch
   - Create pull request via `gh pr create`
4. Clean up env file (Jenkins only)
