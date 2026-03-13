# pyproject.toml — CLI Tool Template (superset of library)

Replace all `ALL_CAPS` placeholders before use.
`CLI_COMMAND` = the console-script name (e.g. `my-tool`).
`CLI_MODULE` = dotted path to the entry function (e.g. `PACKAGE_NAME.cli:main`).

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "PROJECT_NAME"
version = "0.1.0"
description = "PROJECT_DESCRIPTION"
readme = "README.md"
license = { text = "CC BY-NC-SA 4.0" }
authors = [
  { name = "AUTHOR_NAME", email = "AUTHOR_EMAIL" },
]
keywords = []
classifiers = [
  "Development Status :: 3 - Alpha",
  "Environment :: Console",
  "Intended Audience :: Developers",
  "License :: Other/Proprietary License",
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3.11",
  "Programming Language :: Python :: 3.12",
  "Programming Language :: Python :: 3.13",
  "Typing :: Typed",
]
requires-python = ">=PYTHON_MIN"
dependencies = []

[project.scripts]
CLI_COMMAND = "CLI_MODULE"          # e.g. my-tool = "mypackage.cli:main"

[project.optional-dependencies]
dev = [
  "pytest>=8",
  "pytest-cov>=5",
  "ruff>=0.9",
  "mypy>=1.10",
]

[project.urls]
Homepage = "https://github.com/GITHUB_USER/PROJECT_NAME"
Repository = "https://github.com/GITHUB_USER/PROJECT_NAME"
Issues = "https://github.com/GITHUB_USER/PROJECT_NAME/issues"
Changelog = "https://github.com/GITHUB_USER/PROJECT_NAME/blob/main/CHANGELOG.md"

[tool.hatch.build.targets.wheel]
packages = ["src/PACKAGE_NAME"]

# ── Ruff ──────────────────────────────────────────────────────────────────────
[tool.ruff]
src = ["src"]
line-length = 88
target-version = "pyPYTHON_MIN_NODOT"   # e.g. py311

[tool.ruff.lint]
select = [
  "E",   # pycodestyle errors
  "W",   # pycodestyle warnings
  "F",   # pyflakes
  "I",   # isort
  "B",   # flake8-bugbear
  "UP",  # pyupgrade
  "C4",  # flake8-comprehensions
  "SIM", # flake8-simplify
]
ignore = []

[tool.ruff.lint.isort]
known-first-party = ["PACKAGE_NAME"]

# ── Pytest ────────────────────────────────────────────────────────────────────
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--tb=short -q"

# ── Mypy ──────────────────────────────────────────────────────────────────────
[tool.mypy]
python_version = "PYTHON_MIN"
strict = false
warn_return_any = true
warn_unused_configs = true
ignore_missing_imports = true
```

## CLI entry point scaffold

Seed `src/PACKAGE_NAME/cli.py`:

```python
"""CLI entry point for PROJECT_NAME."""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="CLI_COMMAND",
        description="PROJECT_DESCRIPTION",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    # TODO: add subcommands / arguments here
    args = parser.parse_args(argv)
    _ = args  # remove when arguments are used
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
