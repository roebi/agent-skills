---
name: project-bootstrap-en
description: For a given software project goal, recommend the best local LLM model and the skills needed to start implementation. Covers CLI tools, Python libraries, and similar projects.
---

# project-bootstrap Skill

When the user describes a software project they want to build,
produce a structured bootstrap plan covering:

1. **Recommended LLM model** for this task
2. **Required skills** to implement it
3. **Suggested project structure**
4. **First implementation step**

---

## Step 1 — Understand the project

Ask or infer:
- What is the output? (CLI tool, Python library, web service, ...)
- What is the target platform? (Linux, cross-platform, container, ...)
- What is the complexity? (single file, multi-module, subcommands, ...)
- Are there existing libraries to wrap or is this greenfield?

---

## Step 2 — Recommend a model

Use this decision table:

| Task type | Recommended model size | Reason |
|---|---|---|
| Simple CLI, single command | 7B (e.g. qwen2.5-coder-7b) | Skills carry the knowledge |
| Python library, multi-module | 14B (e.g. qwen2.5-coder-14b) | Needs more reasoning across files |
| CLI with subcommands (git/podman style) | 14B-32B | Complex architecture decisions |
| New language / unfamiliar domain | 32B+ or cloud model | Less skill coverage available |

**Key insight:** the richer the skill library, the smaller the model can be.
Skills compensate for model size by providing domain knowledge externally.

---

## Step 3 — Search and recommend skills

For a **Python CLI tool with subcommands** (like git or podman), recommend:

### Essential skills
- `python-project-structure` — src layout, pyproject.toml, hatchling
- `click-cli` — Click framework for subcommands, options, arguments
- `python-testing` — pytest structure, fixtures, coverage
- `git-workflow` — branch naming, commit conventions, PR flow

### Recommended skills
- `datetime-format` — consistent timestamp format across the tool
- `python-logging` — structured logging for CLI tools
- `semver-bump` — version management for releases
- `pypi-publish` — packaging and publishing to PyPI

### Optional skills
- `python-refactoring` — code quality improvement
- `docker-containerfile` — if the tool needs container support
- `github-actions-ci` — CI/CD pipeline

Check available skills first:
```bash
aider-skills list ./skills
```

If a needed skill is missing, create it:
```bash
mkdir -p skills/<skill-name>
# write SKILL.md following the agentskills spec
aider-skills validate skills/<skill-name>
```

---

## Step 4 — Generate project structure

For a Python CLI with subcommands (example: `mytool`):

```
mytool/
├── .devcontainer/
│   └── maintainer/
│       ├── Containerfile
│       ├── devcontainer.json
│       └── scripts/
│           ├── build.sh
│           ├── run.sh
│           └── post-create.sh
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── publish.yml
├── src/
│   └── mytool/
│       ├── __init__.py
│       ├── cli.py          ← click group + subcommands
│       ├── commands/
│       │   ├── __init__.py
│       │   ├── init.py     ← mytool init
│       │   ├── run.py      ← mytool run
│       │   └── status.py   ← mytool status
│       └── core/
│           ├── __init__.py
│           └── engine.py   ← business logic, separate from CLI
├── tests/
│   ├── __init__.py
│   ├── test_cli.py
│   └── test_engine.py
├── skills/                 ← project-local skills
│   └── mytool-conventions/
│       └── SKILL.md
├── pyproject.toml
├── README.md
├── CHANGELOG.md
└── LICENSE
```

---

## Step 5 — First implementation step

Generate the skeleton in this order:

```bash
# 1. Start aider with all needed skills
aider --read $(aider-skills tmpfile ./skills)

# 2. Ask aider to scaffold
# "Create the pyproject.toml and cli.py skeleton for a Click CLI
#  called mytool with subcommands: init, run, status"

# 3. Validate
aider-skills validate ./skills/mytool-conventions

# 4. Run first tests
pytest --tb=short
```

---

## Example: bootstrap a podman-style CLI

```
Goal: build a CLI tool called 'kontainer' with subcommands:
  kontainer build   → build a container image
  kontainer run     → run a container
  kontainer ps      → list running containers
  kontainer stop    → stop a container

Platform: Linux, Python, wrap podman underneath
```

**Recommended model:** qwen2.5-coder-14b (subcommand architecture needs reasoning)

**Skills needed:**
- `click-cli` (subcommand routing)
- `python-project-structure` (src layout)
- `python-subprocess` (wrapping podman commands)
- `python-testing` (mock subprocess calls)
- `semver-bump` + `pypi-publish` (release)

**First aider prompt:**
```
Create a Click CLI called 'kontainer' with four subcommands:
build, run, ps, stop. Each subcommand should call the equivalent
podman command via subprocess. Follow src layout with pyproject.toml.
```

---

## Meta-skill note

This skill itself is a **Level 2 cascading skill** —
it references and composes other skills rather than implementing directly.
It is a *planning* skill, not an *execution* skill.

The agent reads this skill, builds a plan, then activates
each referenced skill in sequence to implement the solution.
