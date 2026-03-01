---
name: skill-container-proxy
description: 'Proxy for skill-container by observerw. Creates new Agent Skills or migrates existing ones into the Skill Container
  format: OCI containers published to GHCR with a CLI entrypoint, a Containerfile, and GitHub-based distribution. Use when
  you want to create a new containerized skill, migrate a plain Agent Skill to Skill Container format, or package a skill
  for portable cross-platform distribution. Trigger phrases: "create skill container", "containerize this skill", "migrate
  skill to container", "package skill as OCI". Use exactly as you would use skill-container directly.'
license: Apache-2.0
metadata:
  proxy-source: https://github.com/observerw/skill-container/blob/main/SKILL.md
  proxy-raw-url: https://raw.githubusercontent.com/observerw/skill-container/86c7fa73afb55abd998f42a1e0b4ab99145f643f/SKILL.md
  proxy-commit: 86c7fa73afb55abd998f42a1e0b4ab99145f643f
  proxy-sha256: 417d26a83253748812bf8ad5537461257b7fe739d0508cd242dea3f59493f432
  proxy-branch: main
  proxy-created-by: roebi
  proxy-created-at: '20260301_0915'
---

# skill-container (proxied from observerw/skill-container)

**Source:** [observerw/skill-container](https://github.com/observerw/skill-container/blob/main/SKILL.md) · branch `main` · commit `86c7fa73afb5`

## ⚠️ Liability disclaimer

The creator of the 'Skill Proxy' is not liable for any damages arising
from the use of this 'Skill Proxy'. The risk and responsibility lies
exclusively with the user who uses this 'Skill Proxy'. If the 'Skill Proxy'
user is an agent, then the user who is responsible for that agent bears
the responsibility.

## ⚠️ Verify before use

Before following any instructions, fetch and verify the remote skill:

1. Fetch the pinned content:
   `https://raw.githubusercontent.com/observerw/skill-container/86c7fa73afb55abd998f42a1e0b4ab99145f643f/SKILL.md`

2. Compute SHA-256 of the fetched content and verify it equals:
   `417d26a83253748812bf8ad5537461257b7fe739d0508cd242dea3f59493f432`

3. If the checksum does **not** match: **STOP immediately.**
   Do not follow any instructions. Alert the user:
   > "The remote skill content has changed unexpectedly. The 'Skill Proxy'
   > checksum does not match. Run `verify-proxy.py` and review before proceeding."

4. If the checksum **matches**: follow the instructions in the fetched SKILL.md.

## Summary (updated 20260301_0915)

This skill shows how to author new skills and migrate legacy `scripts/` skills so they ship a reproducible runtime via Containerfile + published image (typically GHCR), while keeping SKILL.md lean and executable.

## Re-verifying and updating this 'Skill Proxy'

```bash
uv run scripts/verify-proxy.py --proxy ./skills/skill-container-proxy
uv run scripts/update-proxy.py --proxy ./skills/skill-container-proxy
```
