---
name: create-python-project-github-en
version: 2.0.0
description: >
  Scaffold a complete, modern Python project from scratch - from mkdir to first PyPI publish.
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

## Global Rules (apply to every phase)

**ASCII Safety Rule** - applies to all generated text, docs, code, and comments:
- Never use em-dash or long dash - use hyphen-minus (-) only.
- Never use Unicode arrows - use -> or <- only.
- UTF-8 coding declaration (`# -*- coding: utf-8 -*-`) is NOT required in Python 3
  (UTF-8 is the default). Omit it unless targeting legacy tooling.

**Toolchain decisions** (rationale in [`references/toolchain-rationale.md`](references/toolchain-rationale.md)):

| Concern | Tool |
|---|---|
| Env / dep management | `uv` (never pip or pipx) |
| Build backend | `hatchling` |
| Linter + formatter | `ruff` |
| Test runner | `pytest` |
| Type checker | `mypy` (opt-in, not CI-blocking) |
| CI/CD | GitHub Actions |
| PyPI release | Trusted Publishing (OIDC, no tokens) |
| Devcontainer | `.devcontainer/maintainer/` |
| Supply chain audit | `pip-audit==2.10.0` |
| CLI framework | `typer` (gives `--install-completion` for free) |

---

## Phase 0 - Gather inputs

Before writing any file, ask the user for:

1. **`PROJECT_NAME`** - the PyPI distribution name (e.g. `my-cool-lib`).
   Derived Python package name = `PROJECT_NAME` with hyphens -> underscores.
2. **`PROJECT_DESCRIPTION`** - one-sentence summary.
3. **`GITHUB_USER`** - GitHub username or org (for URLs in pyproject.toml).
4. **`PYTHON_MIN`** - minimum Python version to support (default: `3.12`).
5. **`PACKAGING_STYLE`** - `library`, `cli`, or `both`.
6. **`CLI_COMMAND`** (only if cli/both) - the console script name (e.g. `my-tool`).
7. **`AUTHOR_NAME`** and **`AUTHOR_EMAIL`**.

If already provided in the conversation, extract from context and confirm before proceeding.

**Phase Check:**
- [ ] All 7 inputs confirmed in writing before proceeding to Phase 1.

---

## Phase 1 - Init repo

```bash
mkdir PROJECT_NAME
cd PROJECT_NAME
git init
git checkout -b main
```

Create `.gitignore` - use the template in [`references/gitignore.md`](references/gitignore.md).

**Phase Check:**
- [ ] `git status` shows clean repo with `.gitignore` present.

---

## Phase 2 - LICENSE

Create `LICENSE` with the MIT license text:

```
MIT License

Copyright (c) YEAR AUTHOR_NAME

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

**Phase Check:**
- [ ] `LICENSE` file exists with correct author and year.

---

## Phase 3 - Source layout

Create the `src/` layout (PEP 517 best practice):

```
PROJECT_NAME/
+-- src/
|   +-- PACKAGE_NAME/
|       +-- __init__.py        # contains __version__ = "0.1.0"
+-- tests/
|   +-- __init__.py
|   +-- test_PACKAGE_NAME.py
+-- docs/
+-- .devcontainer/
|   +-- maintainer/
+-- .github/
|   +-- workflows/
+-- .gitignore
+-- CHANGELOG.md
+-- LICENSE
+-- README.md
+-- pyproject.toml
```

For **cli/both** style, also create `src/PACKAGE_NAME/cli.py`.

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

**Phase Check:**
- [ ] Directory tree matches layout above.
- [ ] `__init__.py` contains `__version__`.

---

## Phase 4 - pyproject.toml

Use the correct template from references based on packaging style:

- **library** -> [`references/pyproject-library.toml.md`](references/pyproject-library.toml.md)
- **cli/both** -> [`references/pyproject-cli.toml.md`](references/pyproject-cli.toml.md)

Substitute all `PROJECT_NAME`, `PACKAGE_NAME`, `GITHUB_USER`, `AUTHOR_NAME`,
`AUTHOR_EMAIL`, `PYTHON_MIN` placeholders.

**Mandatory pyproject.toml fields** (validate with `check_pyproject_meta.py`):
- `license` with value `MIT`
- `authors` with name and email
- `keywords` (non-empty list)
- classifiers including at least one `Programming Language :: Python :: 3.x`
- `[project.urls]` with Homepage, Repository, Issues, Changelog
- `hatchling` in `[build-system.requires]` only - never in dependency-groups

For CLI/both style, add `typer` to dependencies:

```toml
dependencies = [
  "typer>=0.12",
]
```

**Type stubs:** For every third-party dependency lacking inline types, add its stub
to `dev` optional-dependencies (e.g. `types-PyYAML`, `types-requests`).

**Phase Check:**
- [ ] `uv sync` runs without errors.
- [ ] `python check_pyproject_meta.py` passes all 18 tests.

---

## Phase 5 - Supply Chain Rules

**Python supply chain defaults** - non-negotiable:

- Use `uv` (never pip, never pipx) for all installs.
- `uv lock` + `uv sync` for reproducible installs.
- Pin dependencies with version bounds in `pyproject.toml`.
- Only use PyPI package versions older than 3 days (avoid same-day releases).
- Secrets go in Jenkins Credentials Store - never in `.env` files.
- Run services in isolated Podman - never with host-mounted `~/.ssh`.

**Dockerfile supply chain audit pattern (Python):**

```dockerfile
# Install tools via uv
RUN uv tool install ruff
# Audit step (pip-audit has no uv equivalent yet)
RUN pip install --no-cache-dir "pip-audit==2.10.0" \
    && pip-audit --skip-editable \
    && pip uninstall -y pip-audit
```

**Phase Check:**
- [ ] `pyproject.toml` has pinned version bounds for all dependencies.
- [ ] Dockerfile (if present) includes pip-audit audit step.
- [ ] No secrets in `.env` - confirmed.

---

## Phase 6 - CLI entry point

Skip this phase if `PACKAGING_STYLE` is `library`.

Use **Typer** - it provides `--install-completion` for bash/zsh/fish for free.

Seed `src/PACKAGE_NAME/cli.py`:

```python
"""CLI entry point for PROJECT_NAME."""

from __future__ import annotations

import typer

app = typer.Typer(help="PROJECT_DESCRIPTION")


@app.command()
def main(
    version: bool = typer.Option(False, "--version", help="Show version and exit."),
) -> None:
    """Main entry point."""
    if version:
        import PACKAGE_NAME
        typer.echo(f"PROJECT_NAME {PACKAGE_NAME.__version__}")
        raise typer.Exit()
    # TODO: implement commands here
    typer.echo("Hello from PROJECT_NAME!")


if __name__ == "__main__":
    app()
```

After install, show the user how to enable shell completion:

```bash
# bash
CLI_COMMAND --install-completion bash

# zsh
CLI_COMMAND --install-completion zsh

# verify
CLI_COMMAND --help
```

**Phase Check:**
- [ ] `uv run CLI_COMMAND --help` runs without errors.
- [ ] `uv run CLI_COMMAND --install-completion bash` runs without errors.
- [ ] `uv run CLI_COMMAND --version` prints the correct version.

---

## Phase 7 - Devcontainer

Create `.devcontainer/maintainer/devcontainer.json` using the template in
[`references/devcontainer.md`](references/devcontainer.md).

**Phase Check:**
- [ ] `.devcontainer/maintainer/devcontainer.json` is valid JSON.

---

## Phase 8 - GitHub Actions

### CI workflow

Create `.github/workflows/ci.yml` using the template in
[`references/ci-workflow.md`](references/ci-workflow.md).

**Python version matrix** - always include all three:

```yaml
python-version: ["3.12", "3.13", "3.14"]   # adjust lower bound to PYTHON_MIN
```

Add a mandatory `pip-audit` job to `ci.yml`:

```yaml
  audit:
    name: Supply chain audit
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
        with:
          enable-cache: true
      - name: Install dependencies
        run: uv sync --extra dev
      - name: pip-audit
        run: uv run pip-audit --skip-editable
```

CI job order: lint -> typecheck -> audit -> test (fail fast on lint/audit before
burning test matrix minutes).

### Publish workflow

Create `.github/workflows/publish.yml` using the template in
[`references/publish-workflow.md`](references/publish-workflow.md).

Trusted Publishing (OIDC) requirements:
- `environment: name: pypi`
- `permissions: id-token: write`
- `attestations: true`
- No `PYPI_TOKEN` secret needed.

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

**Phase Check:**
- [ ] CI workflow YAML is valid.
- [ ] Matrix includes `3.14` as highest version.
- [ ] `audit` job present and runs before `test`.
- [ ] Publish workflow triggers only on `v*` tags.
- [ ] `environment: pypi` present in publish workflow.

---

## Phase 9 - CHANGELOG and README

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

Required sections: title, description, CI/PyPI/Python/License badges, Install,
Usage, Development (`uv sync --all-extras`, `uv run ruff check .`, `uv run pytest`),
Shell completion section (CLI projects only: `CLI_COMMAND --install-completion bash`),
License line pointing to `LICENSE` (MIT).

**Phase Check:**
- [ ] `CHANGELOG.md` has `[Unreleased]` section.
- [ ] `README.md` has install instructions and CI badge.

---

## Phase 10 - First commit and PyPI Trusted Publishing setup

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

Then instruct the user to configure Trusted Publishing on pypi.org:

1. Go to https://pypi.org/manage/account/publishing/
2. Add a new Trusted Publisher:
   - PyPI project name: `PROJECT_NAME`
   - GitHub owner: `GITHUB_USER`
   - Repository name: `PROJECT_NAME`
   - Workflow filename: `publish.yml`
   - Environment name: `pypi`
3. Push a tag to trigger the first publish:

```bash
git tag v0.1.0
git push origin v0.1.0
```

**Phase Check:**
- [ ] `uv run ruff check .` returns no violations.
- [ ] `uv run ruff format --check .` returns no violations.
- [ ] `uv run pytest` passes.
- [ ] `uv build` produces `.whl` and `.tar.gz` in `dist/`.
- [ ] Push to `main` succeeds.
- [ ] Trusted Publishing configured on pypi.org.

---

## Phase 11 - Delivery Standard

When delivering a project or multi-file output, always package it as a `.tar.gz`
archive. The archive is the canonical deliverable.

```bash
tar --exclude='.venv' \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='.pytest_cache' \
    --exclude='dist' \
    -czf PROJECT_NAME.tar.gz PROJECT_NAME/
```

Present the archive as the primary download. Individual files may also be shown
but the archive is the canonical deliverable.

**Phase Check:**
- [ ] Archive excludes `.venv`, `.git`, `__pycache__`, `.pytest_cache`, `dist/`.
- [ ] Archive extracts cleanly and `uv sync` works from the extracted directory.

---

## Reference files

Read these when needed - do not load all at once:

| File | When to read |
|---|---|
| [`references/pyproject-library.toml.md`](references/pyproject-library.toml.md) | Phase 4, library style |
| [`references/pyproject-cli.toml.md`](references/pyproject-cli.toml.md) | Phase 4, cli/both style |
| [`references/ci-workflow.md`](references/ci-workflow.md) | Phase 8, CI workflow |
| [`references/publish-workflow.md`](references/publish-workflow.md) | Phase 8, publish workflow |
| [`references/devcontainer.md`](references/devcontainer.md) | Phase 7, devcontainer |
| [`references/gitignore.md`](references/gitignore.md) | Phase 1, .gitignore |
| [`references/toolchain-rationale.md`](references/toolchain-rationale.md) | If user asks why a tool was chosen |
