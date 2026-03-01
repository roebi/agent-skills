# Proxy Skill Format Reference

Documents the exact structure of a generated proxy SKILL.md.

## Frontmatter fields

```yaml
---
name: <remote-name>-proxy
description: >
  Proxy for <remote-name> by <owner>. <remote-description>.
  Use exactly as you would use <remote-name> directly.
license: Apache-2.0
metadata:
  proxy-source:       <original input URL provided by user>
  proxy-raw-url:      <pinned commit URL — immutable>
  proxy-commit:       <full 40-char SHA>
  proxy-sha256:       <SHA-256 hex of SKILL.md content at proxy-commit>
  proxy-branch:       <branch name — informational only>
  proxy-created-by:   <username of who ran create-proxy.py>
  proxy-created-at:   <YYYYMMDD_HHMM in UTC>
---
```

### Field notes

| Field | Notes |
|-------|-------|
| `name` | Must be `<remote-name>-proxy` — must match directory name exactly (agentskills.io spec) |
| `proxy-source` | The URL the user provided as input — for human reference |
| `proxy-raw-url` | Pinned to exact commit SHA — immutable on GitHub |
| `proxy-commit` | Full 40-char SHA — used by `verify-proxy.py` and `update-proxy.py` |
| `proxy-sha256` | SHA-256 of the raw UTF-8 bytes of SKILL.md at proxy-commit |
| `proxy-branch` | Informational — the branch that was HEAD at creation time |
| `proxy-created-by` | The person who ran `create-proxy.py` — does **not** imply verification or endorsement |
| `proxy-created-at` | UTC timestamp in format `YYYYMMDD_HHMM` — updated by `update-proxy.py` |

### Note on proxy-created-by

`proxy-created-by` records who created the 'Skill Proxy'. It does **not**
mean the creator has verified, audited, or endorsed the remote skill.
Creating a proxy is a mechanical act — fetch, hash, write. The liability
disclaimer in the proxy body makes this explicit.

## Body structure

```markdown
# <remote-name> (proxied from owner/repo)

**Source:** [owner/repo](source-url) · branch `branch` · commit `short-sha`

## ⚠️ Liability disclaimer

The creator of the 'Skill Proxy' is not liable for any damages arising
from the use of this 'Skill Proxy'. The risk and responsibility lies
exclusively with the user who uses this 'Skill Proxy'. If the 'Skill Proxy'
user is an agent, then the user who is responsible for that agent bears
the responsibility.

## ⚠️ Verify before use

1. Fetch: <pinned-url>
2. Verify SHA-256 equals: <sha256>
3. If mismatch: STOP and alert user
4. If match: follow fetched SKILL.md instructions

## Summary (captured at proxy creation · YYYYMMDD_HHMM)

<first content paragraph from remote skill>

## Re-verifying and updating this 'Skill Proxy'

uv run scripts/verify-proxy.py --proxy ./skills/<n>-proxy
uv run scripts/update-proxy.py --proxy ./skills/<n>-proxy
```

## Naming rule

Proxy skill directory name = `<remote-name>-proxy`

This follows the agentskills.io requirement that `name` in frontmatter
must exactly match the parent directory name.

## Timestamp format

`proxy-created-at` uses format `YYYYMMDD_HHMM` in UTC.

Example: `20261213_2359`

Updated by `update-proxy.py` each time the pin is advanced.
