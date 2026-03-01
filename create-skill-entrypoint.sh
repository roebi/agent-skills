#!/bin/bash
# create-skill-entrypoint.sh
# Shared entrypoint for both tide-skills (Jenkins/LiteLLM) and agent-skills (GitHub Actions/GitHub Models).
# All configuration is via environment variables — no secrets baked in.
#
# Required env vars:
#   SKILL_NAME          — new skill name (lowercase, hyphens only)
#   SKILL_DOES          — what the skill does
#   SKILL_WHEN          — when to use it
#   SKILL_KEYWORDS      — comma-separated keywords
#   CREATOR_SKILL_URL   — URL of the creator skill (any GitHub URL form)
#   MODEL               — model name (auto-resolved against LiteLLM if OPENAI_API_BASE is set)
#   GIT_REPO_URL        — target git repo HTTPS URL
#   FEATURE_BRANCH      — feature branch name to create
#   GIT_USER_NAME       — git commit author name
#   GIT_USER_EMAIL      — git commit author email
#   GH_TOKEN            — GitHub token for git push and gh pr create
#   OPENAI_API_KEY      — API key (GitHub Models token or LiteLLM key)
#   OPENAI_API_BASE     — API base URL (GitHub Models or LiteLLM endpoint)

set -euo pipefail

echo "========================================================"
echo "  create-skill pipeline"
echo "========================================================"
echo "  Skill name    : ${SKILL_NAME}"
echo "  Feature branch: ${FEATURE_BRANCH}"
echo "  Target repo   : ${GIT_REPO_URL}"
echo "  Model (raw)   : ${MODEL}"
echo "  Creator skill : ${CREATOR_SKILL_URL}"
echo "========================================================"


# ── Step 1: Resolve model name ───────────────────────────────────────────────
# If OPENAI_API_BASE is set, query LiteLLM /v1/models and find the exact
# registered model name that matches the MODEL parameter value.
# Falls back to using MODEL as-is if resolution fails.

echo ""
echo "Step 1: Resolving model name..."

RESOLVED_MODEL=$(python3 - <<'PYEOF'
import sys, json, os
import urllib.request

base = os.environ.get("OPENAI_API_BASE", "").rstrip("/")
key  = os.environ.get("OPENAI_API_KEY", "")
target = os.environ.get("MODEL", "")

if not base:
    print(target)
    sys.exit(0)

try:
    req = urllib.request.Request(
        f"{base}/v1/models",
        headers={"Authorization": f"Bearer {key}"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.load(resp)

    models = [m["id"] for m in data.get("data", [])]
    # Match exact, with openai/ prefix, or as suffix
    for m in models:
        if m == target or m.endswith("/" + target) or m.endswith("-" + target):
            print(m)
            sys.exit(0)

    print(f"Warning: model '{target}' not found in LiteLLM. Available: {models}", file=sys.stderr)
    print(target)

except Exception as e:
    print(f"Warning: model resolution failed ({e}), using raw value: {target}", file=sys.stderr)
    print(target)
PYEOF
)

echo "  Resolved model: ${RESOLVED_MODEL}"


# ── Step 2: Configure git ────────────────────────────────────────────────────
echo ""
echo "Step 2: Configuring git..."

git config --global user.name  "${GIT_USER_NAME}"
git config --global user.email "${GIT_USER_EMAIL}"
# Use token for HTTPS auth — avoids ssh key setup
git config --global credential.helper store
# Strip protocol from GIT_REPO_URL to insert token
REPO_HOST=$(echo "${GIT_REPO_URL}" | sed 's|https://||')
echo "https://x-token:${GH_TOKEN}@github.com" > ~/.git-credentials
chmod 600 ~/.git-credentials

echo "  ✓ git configured as ${GIT_USER_NAME} <${GIT_USER_EMAIL}>"


# ── Step 3: Clone repo ───────────────────────────────────────────────────────
echo ""
echo "Step 3: Cloning ${GIT_REPO_URL} ..."

# Insert token into clone URL
CLONE_URL=$(echo "${GIT_REPO_URL}" | sed "s|https://|https://x-token:${GH_TOKEN}@|")
git clone "${CLONE_URL}" /workspace/repo
cd /workspace/repo

echo "  ✓ Cloned to /workspace/repo"


# ── Step 4: Create feature branch ───────────────────────────────────────────
echo ""
echo "Step 4: Creating feature branch ${FEATURE_BRANCH} ..."

git checkout -b "${FEATURE_BRANCH}"
echo "  ✓ On branch ${FEATURE_BRANCH}"


# ── Step 5: Fetch creator skill ──────────────────────────────────────────────
echo ""
echo "Step 5: Fetching creator skill from ${CREATOR_SKILL_URL} ..."

CREATOR_SKILL_TMP=$(mktemp /tmp/creator-skill-XXXXXX.md)
export CREATOR_SKILL_TMP

python3 - <<PYEOF
import os, re, sys
import urllib.request

url = os.environ.get("CREATOR_SKILL_URL", "")

# Translate any GitHub URL form to raw.githubusercontent.com
url = re.sub(
    r'https://github\.com/([^/]+)/([^/]+)/blob/([^/]+)/(.+)',
    r'https://raw.githubusercontent.com/\1/\2/\3/\4',
    url
)
url = re.sub(
    r'https://github\.com/([^/]+)/([^/]+)/tree/([^/]+)/(.+)',
    r'https://raw.githubusercontent.com/\1/\2/\3/\4/SKILL.md',
    url
)
url = re.sub(
    r'https://github\.com/([^/]+)/([^/]+)/tree/([^/]+)$',
    r'https://raw.githubusercontent.com/\1/\2/\3/SKILL.md',
    url
)
url = re.sub(
    r'https://github\.com/([^/]+)/([^/]+)$',
    r'https://raw.githubusercontent.com/\1/\2/main/SKILL.md',
    url
)

try:
    with urllib.request.urlopen(url, timeout=15) as resp:
        content = resp.read().decode("utf-8")
    with open(os.environ["CREATOR_SKILL_TMP"], "w") as f:
        f.write(content)
    print(f"  ✓ Fetched creator skill ({len(content)} bytes) from {url}")
except Exception as e:
    print(f"  Error fetching creator skill: {e}", file=sys.stderr)
    sys.exit(1)
PYEOF


# ── Step 6: Build aider-skills context ──────────────────────────────────────
echo ""
echo "Step 6: Building aider-skills context..."

SKILL_CONTEXT_ARG=""
if [[ -d "./skills" ]]; then
    SKILL_CONTEXT=$(aider-skills tmpfile ./skills 2>/dev/null || echo "")
    if [[ -n "${SKILL_CONTEXT}" ]]; then
        SKILL_CONTEXT_ARG="--read ${SKILL_CONTEXT}"
        echo "  ✓ aider-skills context: ${SKILL_CONTEXT}"
    fi
else
    echo "  (no ./skills directory found — skipping aider-skills context)"
fi


# ── Step 7: Write aider message to temp file ─────────────────────────────────
echo ""
echo "Step 7: Preparing aider message..."

MSG_FILE=$(mktemp /tmp/aider-msg-XXXXXX.txt)
cat > "${MSG_FILE}" << MSGEOF
Read the creator skill instructions from the context file first.

Create a new Agent Skill with the following specification,
following the agentskills.io specification for all fields:

name: ${SKILL_NAME}

skill does: ${SKILL_DOES}

skill when to use it: ${SKILL_WHEN}

keywords: ${SKILL_KEYWORDS}

Instructions:
- Combine 'skill does' and 'skill when to use it' into the SKILL.md
  description field, following the agentskills.io specification.
- Include the keywords naturally in the description so agents can
  identify relevant tasks.
- Write the skill into skills/${SKILL_NAME}/SKILL.md only.
- Do not create or modify any other files.
MSGEOF

echo "  ✓ Message written to ${MSG_FILE}"


# ── Step 8: Run aider ────────────────────────────────────────────────────────
echo ""
echo "Step 8: Running aider to create skill ${SKILL_NAME} ..."

# Create the target file so aider knows what to write
mkdir -p "skills/${SKILL_NAME}"
touch "skills/${SKILL_NAME}/SKILL.md"

aider \
    --model "${RESOLVED_MODEL}" \
    --read "${CREATOR_SKILL_TMP}" \
    ${SKILL_CONTEXT_ARG} \
    --message "$(cat "${MSG_FILE}")" \
    --yes \
    --no-auto-commits \
    "skills/${SKILL_NAME}/SKILL.md"

echo "  ✓ aider completed"


# ── Step 9: Validate generated skill ────────────────────────────────────────
echo ""
echo "Step 9: Validating generated skill..."

if command -v aider-skills &>/dev/null; then
    aider-skills validate "./skills/${SKILL_NAME}" \
        && echo "  ✓ aider-skills validate passed" \
        || echo "  ⚠ aider-skills validate reported issues — review before merging"
elif command -v skills-ref &>/dev/null; then
    skills-ref validate "./skills/${SKILL_NAME}" \
        && echo "  ✓ skills-ref validate passed (fallback — demo tool)" \
        || echo "  ⚠ skills-ref validate reported issues — review before merging"
else
    echo "  (no validator found — skipping)"
fi


# ── Step 10: Commit ──────────────────────────────────────────────────────────
echo ""
echo "Step 10: Committing..."

git add "skills/${SKILL_NAME}/"

if git diff --staged --quiet; then
    echo "  ERROR: no changes staged — aider may not have created the skill file"
    echo "  Check the aider output above for errors."
    exit 1
fi

git commit -m "feat(skill): add ${SKILL_NAME} [${FEATURE_BRANCH}]"
echo "  ✓ Committed"


# ── Step 11: Push ────────────────────────────────────────────────────────────
echo ""
echo "Step 11: Pushing ${FEATURE_BRANCH} ..."

git push origin "${FEATURE_BRANCH}"
echo "  ✓ Pushed"


# ── Step 12: Create PR ───────────────────────────────────────────────────────
echo ""
echo "Step 12: Creating pull request..."

gh pr create \
    --base main \
    --head "${FEATURE_BRANCH}" \
    --title "feat(skill): add ${SKILL_NAME}" \
    --body "## New Skill: \`${SKILL_NAME}\`

**Does:** ${SKILL_DOES}

**When to use:** ${SKILL_WHEN}

**Keywords:** \`${SKILL_KEYWORDS}\`

---

**Creator skill:** ${CREATOR_SKILL_URL}
**Model used:** ${RESOLVED_MODEL}
**Branch:** \`${FEATURE_BRANCH}\`

*Created by create-skill pipeline*"

echo "  ✓ Pull request created"

echo ""
echo "========================================================"
echo "  ✓ create-skill pipeline complete"
echo "  Skill : ${SKILL_NAME}"
echo "  Branch: ${FEATURE_BRANCH}"
echo "========================================================"
