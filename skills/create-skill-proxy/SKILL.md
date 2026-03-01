---
name: create-skill-proxy
description: >
  Creates a local proxy skill that wraps a remote Agent Skill from any
  GitHub repository. The proxy pins the remote skill to an exact commit
  hash and SHA-256 checksum so the agent verifies content integrity on
  every use. Use when a user wants to add an external skill to their
  skill library, proxy a remote skill, pin and trust a skill from GitHub,
  or wrap a foreign skill safely. Trigger phrases: "proxy this skill",
  "add external skill", "wrap remote skill", "pin this skill from GitHub".
license: Apache-2.0
compatibility: Requires Python 3.11+, uv, and internet access to GitHub.
metadata:
  author: roebi
  repo: https://github.com/roebi/agent-skills
---

# Create Skill Proxy

Creates a local `<n>-proxy` skill that wraps a remote Agent Skill.

## ⚠️ Liability disclaimer

The creator of the 'Skill Proxy' is not liable for any damages arising
from the use of this 'Skill Proxy'. The risk and responsibility lies
exclusively with the user who uses this 'Skill Proxy'. If the 'Skill Proxy'
user is an agent, then the user who is responsible for that agent bears
the responsibility.

## What this skill does

The proxy pins the remote skill to a specific commit hash and SHA-256
checksum. Every time the agent activates the proxy, it fetches the remote
SKILL.md and verifies the checksum before following any instructions.
If the checksum does not match, the agent stops and alerts the user.

This follows the Page Object Pattern — the proxy hides where a skill lives
while keeping all trusted external skills in one place under your control.

## Inputs

| Parameter | Required | Description |
|-----------|----------|-------------|
| `REMOTE_URL` | Yes | Any GitHub URL pointing to the remote skill (see URL forms below) |
| `OUTPUT_DIR` | No | Parent directory to write the proxy skill into (default: `./skills`) |

## Accepted URL forms

All five forms are accepted and translated automatically:

| Input form | Example |
|-----------|---------|
| Repo root | `https://github.com/observerw/skill-container` |
| Tree root | `https://github.com/observerw/skill-container/tree/main` |
| Tree path | `https://github.com/observerw/skill-container/tree/main/skills/my-skill` |
| Blob file | `https://github.com/observerw/skill-container/blob/main/SKILL.md` |
| Raw URL | `https://raw.githubusercontent.com/observerw/skill-container/main/SKILL.md` |

## Workflow

```bash
uv run scripts/create-proxy.py \
  --url "https://github.com/observerw/skill-container" \
  --output-dir ./skills
```

The script:
1. Translates input URL to raw content URL (see `references/url-translation.md`)
2. Fetches `SKILL.md` content from remote
3. Validates frontmatter against agentskills.io spec — aborts if invalid
4. Fetches current HEAD commit hash via GitHub API
5. Computes SHA-256 of the fetched content
6. Generates `<n>-proxy/SKILL.md` with pinned commit URL and checksum
7. Runs `skills-ref validate` on the generated proxy skill
8. Prints the created skill path and next steps

## Re-verifying and updating proxies

```bash
# Re-verify: check if remote content still matches pinned checksum
uv run scripts/verify-proxy.py --proxy ./skills/skill-container-proxy

# Update: re-fetch, re-validate, update commit pin and checksum
uv run scripts/update-proxy.py --proxy ./skills/skill-container-proxy
```

Run `verify-proxy.py` periodically or in CI to detect upstream changes.
Run `update-proxy.py` only after consciously reviewing the upstream changes.

## Reference files

- `references/url-translation.md` — full URL translation rules and examples
- `references/proxy-format.md` — exact format of generated proxy SKILL.md
