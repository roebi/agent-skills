---
name: create-python-project-github-en
version: 1.1.0
description: >
  Scaffold a complete, modern Python project from scratch — from `mkdir` to first PyPI publish.
  Use this skill whenever the user wants to create a new Python package, library, CLI tool, or
  PyPI module, start a new Python open-source project, set up GitHub Actions CI/CD for Python,
  or asks how to structure a modern Python project with packaging, testing, and devcontainer.
  Also triggers for "new pypi module", "python project template", "python package from scratch",
  "hatch", "uv init", or any request to bootstrap a Python repo with best practices.
license: CC BY-NC-SA 4.0
language: en
author: roebi (Robert Halter)
attribution: >
  Part of the roebi agent-skills library.
  https://github.com/roebi/agent-skills
spec: https://agentskills.io/specification
---

# Create Python Project (GitHub + PyPI)

Scaffold a complete modern Python project from `mkdir` to first PyPI publish.

**Toolchain decisions** (rationale in [`references/toolchain-rationale.md`](references/toolchain-rationale.md)):

| Concern | Tool |
|---|---|
| Env / dep management | `uv` |
| Build backend | `hatchling` |
| Linter + formatter | `ruff` |
| Test runner | `pytest` |
| Type checker | `mypy` (opt-in, not CI-blocking) |
| CI/CD | GitHub Actions |
| PyPI release | Trusted Publishing (OIDC, no tokens) |
| Devcontainer | `.devcontainer/maintainer/` |

---

## Phase 0 — Gather inputs

Before writing any file, ask the user for:

1. **`PROJECT_NAME`** — the PyPI distribution name (e.g. `my-cool-lib`). Derived Python package name = `PROJECT_NAME` with hyphens → underscores.
2. **`PROJECT_DESCRIPTION`** — one-sentence summary.
3. **`GITHUB_USER`** — GitHub username or org (for URLs in pyproject.toml).
4. **`PYTHON_MIN`** — minimum Python version to support (default: `3.12`).
5. **`PACKAGING_STYLE`** — `library`, `cli`, or `both` (if both, the project exposes both an importable package AND a CLI entry point).
6. **`CLI_COMMAND`** (only if cli/both) — the console script name (e.g. `my-tool`).
7. **`AUTHOR_NAME`** and **`AUTHOR_EMAIL`**.

If the user has already provided these in the conversation, extract from context and confirm before proceeding.

---

## Phase 1 — Init repo

```bash
mkdir PROJECT_NAME
cd PROJECT_NAME
git init
git checkout -b main
```

Create `.gitignore` — use the template in [`references/gitignore.md`](references/gitignore.md).

---

## Phase 2 — Source layout

Create the `src/` layout (PEP 517 best practice, prevents accidental imports from repo root):

```
PROJECT_NAME/
├── src/
│   └── PACKAGE_NAME/          # PACKAGE_NAME = PROJECT_NAME with - replaced by _
│       ├── __init__.py        # contains __version__ = "0.1.0"
│       └── _version.py        # (optional, if using hatch-vcs dynamic versioning)
├── tests/
│   ├── __init__.py
│   └── test_PACKAGE_NAME.py
├── docs/
├── .devcontainer/
│   └── maintainer/
├── .github/
│   └── workflows/
├── .gitignore
├── CHANGELOG.md
├── LICENSE
├── README.md
└── pyproject.toml
```

For **cli/both** style, also create:

```
src/PACKAGE_NAME/
└── cli.py                     # entry point for the console script
```

Seed `src/PACKAGE_NAME/__init__.py`:

```python
"""PROJECT_DESCRIPTION"""

__version__ = "0.1.0"
```

Seed `tests/test_PACKAGE_NAME.py`:

```python
"""Basic smoke tests for PACKAGE_NAME."""

import PACKAGE_NAME


def test_version():
    assert PACKAGE_NAME.__version__ == "0.1.0"
```

---

## Phase 3 — pyproject.toml

Use the correct template from references based on packaging style:

- **library** → [`references/pyproject-library.toml.md`](references/pyproject-library.toml.md)
- **cli** → [`references/pyproject-cli.toml.md`](references/pyproject-cli.toml.md)
- **both** → use the cli template (it includes the library configuration as a superset)

Substitute all `PROJECT_NAME`, `PACKAGE_NAME`, `GITHUB_USER`, `AUTHOR_NAME`, `AUTHOR_EMAIL`, `PYTHON_MIN` placeholders.

**Type stubs:** For every third-party dependency that lacks inline types, add its stub package to the `dev` optional-dependencies. Common ones:

| Dependency | Stub package |
|---|---|
| `pyyaml` | `types-PyYAML` |
| `requests` | `types-requests` |
| `toml` | `types-toml` |

For packages with no stubs available (e.g. `sentence-transformers`), use `# type: ignore[import-untyped]` on the import line — **not** a bare `# type: ignore`, which mypy will flag as unused once stubs are installed.

---

## Phase 4 — Devcontainer

Create `.devcontainer/maintainer/devcontainer.json` using the template in [`references/devcontainer.md`](references/devcontainer.md).

The devcontainer gives any maintainer (or Codespace) a reproducible environment with `uv`, `ruff`, and `pytest` pre-installed.

---

## Phase 5 — GitHub Actions

### CI workflow

Create `.github/workflows/ci.yml` using the template in [`references/ci-workflow.md`](references/ci-workflow.md).

The CI workflow: lints with `ruff check` and `ruff format --check` **before** running tests,
optionally type-checks with `mypy` (non-blocking), then runs `pytest` across a Python version
matrix from `PYTHON_MIN` through `3.13`.

**Python version matrix** (always include all three):

```yaml
python-version: ["3.12", "3.13"]   # adjust lower bound to PYTHON_MIN
```

> If `PYTHON_MIN` is `3.11`, the matrix becomes `["3.11", "3.12", "3.13"]`.

### Publish workflow

Create `.github/workflows/publish.yml` using the template in [`references/publish-workflow.md`](references/publish-workflow.md).

The publish workflow: triggers on `v*` tags, builds with `uv build`, publishes via OIDC Trusted Publishing (no API tokens needed). After creating the file, remind the user to configure Trusted Publishing on pypi.org (see Phase 8).

### Issue triage workflow

Create `.github/workflows/set-label-triage-to-new-issue.yml`:

```yaml
name: Triage new issues
on:
  issues:
    types: [opened]
jobs:
  triage:
    runs-on: ubuntu-latest
    permissions:
      issues: write
    steps:
      - uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.addLabels({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              labels: ['triage']
            })
```

---

## Phase 6 — CHANGELOG and README

### CHANGELOG.md

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - YYYY-MM-DD

### Added
- Initial release
```

### README.md

```markdown
# PROJECT_NAME

PROJECT_DESCRIPTION

[![CI](https://github.com/GITHUB_USER/PROJECT_NAME/actions/workflows/ci.yml/badge.svg)](https://github.com/GITHUB_USER/PROJECT_NAME/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/PROJECT_NAME)](https://pypi.org/project/PROJECT_NAME/)
[![Python](https://img.shields.io/pypi/pyversions/PROJECT_NAME)](https://pypi.org/project/PROJECT_NAME/)
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC_BY--NC--SA_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

## Install

\```
pip install PROJECT_NAME
\```

## Usage

TODO

## Development

\```bash
uv sync --all-extras
uv run ruff check .
uv run ruff format --check .
uv run pytest
\```

## License

CC BY-NC-SA 4.0 — see [LICENSE](LICENSE).
```

---

## Phase 7 — LICENSE

Create `LICENSE` with the full CC BY-NC-SA 4.0 legal text.

Fetch it from: `https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode.txt`

Or write the standard header:

```
Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International

Copyright (c) YEAR AUTHOR_NAME

This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike
4.0 International License. To view a copy of this license, visit
https://creativecommons.org/licenses/by-nc-sa/4.0/ or send a letter to
Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
```

---

## Phase 8 — First commit and PyPI Trusted Publishing setup

```bash
uv sync
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv build
git add .
git commit -m "chore: initial project scaffold"
git remote add origin https://github.com/GITHUB_USER/PROJECT_NAME.git
git push -u origin main
```

Then instruct the user to:

1. Go to https://pypi.org/manage/account/publishing/
2. Add a new Trusted Publisher with:
   - **PyPI project name**: `PROJECT_NAME`
   - **GitHub owner**: `GITHUB_USER`
   - **Repository name**: `PROJECT_NAME`
   - **Workflow filename**: `publish.yml`
   - **Environment name**: `pypi` (must match the workflow's `environment:` field)
3. Push a tag to trigger the first publish:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

---

## Phase 9 — Verification checklist

After scaffolding, verify each item **in this order** (linting before tests):

- [ ] `uv sync` runs without errors
- [ ] `uv run ruff check .` returns no violations
- [ ] `uv run ruff format --check .` returns no violations
- [ ] `uv run mypy src/` passes with no errors (unused `# type: ignore` comments are errors — use `# type: ignore[import-untyped]` for untyped third-party libs)
- [ ] `uv run pytest` passes
- [ ] `uv build` produces a `.whl` and `.tar.gz` in `dist/`
- [ ] CI workflow matrix includes `3.13` as the highest Python version
- [ ] CI workflow file is valid YAML and triggers on `push` and `pull_request`
- [ ] Publish workflow file triggers only on `v*` tags
- [ ] `.devcontainer/maintainer/devcontainer.json` is valid JSON
- [ ] `CHANGELOG.md` exists with `[Unreleased]` section
- [ ] `LICENSE` contains CC BY-NC-SA 4.0 text
- [ ] `README.md` has install instructions and CI badge

---

## Reference files

Read these when needed — do not load all at once:

| File | When to read |
|---|---|
| [`references/pyproject-library.toml.md`](references/pyproject-library.toml.md) | Phase 3, library style |
| [`references/pyproject-cli.toml.md`](references/pyproject-cli.toml.md) | Phase 3, cli/both style |
| [`references/ci-workflow.md`](references/ci-workflow.md) | Phase 5, CI workflow |
| [`references/publish-workflow.md`](references/publish-workflow.md) | Phase 5, publish workflow |
| [`references/devcontainer.md`](references/devcontainer.md) | Phase 4, devcontainer |
| [`references/gitignore.md`](references/gitignore.md) | Phase 1, .gitignore |
| [`references/toolchain-rationale.md`](references/toolchain-rationale.md) | If user asks *why* a tool was chosen |
