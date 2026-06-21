---
name: session-git-lifecycle-en
license: CC BY-NC-SA 4.0
description: >
  Defines the git-based lifecycle for agent chat sessions: CREATE for new
  projects (git init with explicit main branch) and RESUME for continuing
  work from a delivered tar.gz containing a .git folder. Use this skill
  whenever an agent starts a new software project from scratch, or whenever
  a user provides a versioned tar.gz to continue work in a new or resumed
  session. Also covers the handover tag namespace convention (handover/vN)
  that keeps session delivery tags safely separated from software version
  tags (vX.Y.Z) used by GitHub Actions release workflows. Trigger phrases:
  "start new project", "new session", "resume project", "continue from tar",
  "here is myproject_vN.tar.gz", "untar and continue", "pick up where we
  left off", "add github actions release workflow".
metadata:
  author: roebi
  spec: https://agentskills.io/specification
---

# Session Git Lifecycle

Defines two procedures - CREATE and RESUME - that together form the
git-based state management protocol for agent chat sessions.

Every software project an agent works on MUST live in a git repository
from the first commit. Every delivered tar.gz MUST include the full .git
folder so that any future session can reconstitute the complete project
state, history, and intent without additional explanation from the user.

---

## Why git inside the tar.gz

A tar.gz with .git contains four layers of context for a resuming agent:

- `git log` -> what was built, in order, with intent encoded in commit messages
- `git diff` -> exact state of every file at every point in history
- `Handover-State.md` -> known bugs, deferred items, explicit next steps
- conversation history -> decisions and constraints in natural language

This makes every tar.gz a self-contained, agent-resumable project capsule
usable in any session, on any day, without re-explanation.

---

## C - CREATE procedure (new session, new project)

Use when: the user starts a new project from scratch with no prior tar.gz.

```bash
# 1. Create project folder
mkdir <projectname>
cd <projectname>

# 2. Init git repo with explicit main branch
#    Required: git 2.x does NOT default to main.
#    git 3.x will default to main, but we declare it explicitly
#    so the skill works correctly on any git version.
git init -b main

# 3. Create Handover-State.md immediately
cat > Handover-State.md << 'EOF'
# Handover State

## Project
<projectname>

## Status
Session started. No deliveries yet.

## Known issues
None.

## Deferred items
None.

## Next steps
- Define requirements
- Write openapi.json if HTTP endpoints are involved
- Begin TDD cycle
EOF

# 4. Initial commit - repo is now tracked from zero
git add Handover-State.md
git commit -m "init: project start, main branch, Handover-State.md"
```

After this: every file created, every test written, every feature added
gets committed with a meaningful message. The git log becomes the
project diary.

### Commit message convention

```
init:    project start or scaffold
feat:    new feature or endpoint
fix:     bug fix
test:    test additions or changes
refactor: code restructure, no behavior change
docs:    documentation only
chore:   build, config, CI changes
```

### Handover tag at every delivery

Before packaging the tar.gz for delivery, tag the current commit.

Tag namespace rule - two tag families, never mixed:

```
Software version tags:  v1.0.0   v1.2.3   v2.0.0
Handover delivery tags: handover/v1   handover/v2   handover/v3
```

The slash prefix puts handover tags in a separate Git ref namespace:

```
refs/tags/v1.0.0        <- software release, triggers GitHub Actions
refs/tags/handover/v1   <- session delivery snapshot, never triggers release
```

```bash
git tag handover/v<N>
git gc --aggressive
cd ..
tar -czf <projectname>_v<N>.tar.gz <projectname>/
```

The tag anchors the delivery version in git history. `handover/v2` maps
1:1 to `<projectname>_v2.tar.gz`.

---

## R - RESUME procedure (any session, from tar.gz)

Use when: the user provides a versioned tar.gz from a prior delivery.

```bash
# 1. Untar - restores full file tree including .git
tar -xzf <projectname>_v<N>.tar.gz
cd <projectname>

# 2. Read project history - understand what was built and why
git log --oneline

# 3. Read branch structure
git branch -a

# 4. Read explicit handover state
cat Handover-State.md

# 5. Confirm working tree is clean before starting new work
git status
```

After these five commands the agent has complete project context and can
continue work - fix bug, add feature, refactor - as if no interruption
occurred.

### Resume continuation commit

After completing the requested work in a resume session:

```bash
git add .
git commit -m "feat: <what was done in this resume session>"
git tag handover/v<N+1>
git gc --aggressive
cd ..
tar -czf <projectname>_v<N+1>.tar.gz <projectname>/
```

Deliver `<projectname>_v<N+1>.tar.gz`. The version increments. The
history is continuous. The next session can resume again from v(N+1).

---

## GitHub push convention

When the project is promoted to a GitHub repo, push tag namespaces
separately to make intent explicit:

```bash
# push code and handover tags only
git push origin main
git push origin 'refs/tags/handover/*'

# push software release tag separately (triggers GitHub Actions release)
git tag v1.0.0
git push origin 'refs/tags/v*'
```

Never push all tags with `git push origin --tags` - this would push both
namespaces at once and could trigger unintended release workflows.

---

## GitHub Actions release workflow rule

Every GitHub Actions release workflow in a project that uses this skill
MUST restrict its trigger to software version tags only, using an explicit
positive pattern match:

```yaml
# .github/workflows/release.yml
on:
  push:
    tags:
      - 'v[0-9]+.[0-9]+.[0-9]+'
```

This pattern matches: v1.0.0, v2.3.1, v10.0.0
This pattern does NOT match: handover/v1, handover/v2, handover/v3

The handover tag namespace `handover/*` never matches `v[0-9]+.[0-9]+.[0-9]+`
so no explicit exclude is needed. The positive pattern is the complete guard.

Document this intent in the workflow file with a comment:

```yaml
on:
  push:
    tags:
      # Software version releases only.
      # Handover delivery tags (handover/vN) intentionally excluded
      # by this positive pattern - they never match vX.Y.Z format.
      - 'v[0-9]+.[0-9]+.[0-9]+'
```

---

## CRUD mapping

| CRUD | Trigger | Agent first action |
|------|---------|-------------------|
| C | new project, no tar.gz | `git init -b main` + empty commit |
| R | user provides vN.tar.gz | untar + git log + git branch -a + cat Handover-State.md |
| U | "fix bug / add feature" | resume procedure, then work, then deliver v(N+1) |
| D | retire project | user-side action, archive or drop the tar.gz |

U (update) is always a resume followed by a new delivery.
D (delete) is never an agent action.

---

## Constraints

- NEVER start working in an untracked folder. `git init -b main` is the
  first action on every new project, before any code is written.
- NEVER deliver a tar.gz without the .git folder included.
- NEVER deliver a tar.gz without a handover tag on the delivery commit.
- ALWAYS use `handover/vN` tag format - never bare `handover-vN` or `vN`.
- NEVER use `git push origin --tags` - push tag namespaces separately.
- ALWAYS run `git gc --aggressive` before packaging to minimize tar size.
- ALWAYS update Handover-State.md before the delivery commit to reflect
  current known issues and next steps.
- The `-b main` flag is mandatory on `git init`. Do not rely on git
  default branch configuration - it differs between git 2.x and git 3.x.
- EVERY GitHub Actions release workflow MUST trigger only on
  `v[0-9]+.[0-9]+.[0-9]+` pattern. Never on `handover/*`.
