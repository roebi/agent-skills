# Devcontainer Template — Maintainer Environment

File: `.devcontainer/maintainer/devcontainer.json`

Provides a reproducible container environment for maintainers and GitHub Codespaces users.

```json
{
  "name": "PROJECT_NAME maintainer",
  "image": "mcr.microsoft.com/devcontainers/python:1-3.12-bullseye",
  "features": {
    "ghcr.io/devcontainers/features/common-utils:2": {
      "installZsh": true,
      "configureZshAsDefaultShell": true,
      "installOhMyZsh": true,
      "upgradePackages": true
    },
    "ghcr.io/devcontainers/features/git:1": {
      "ppa": true,
      "version": "latest"
    }
  },
  "onCreateCommand": "pip install uv && uv sync --extra dev",
  "postCreateCommand": "uv run pre-commit install 2>/dev/null || true",
  "customizations": {
    "vscode": {
      "settings": {
        "python.defaultInterpreterPath": ".venv/bin/python",
        "editor.formatOnSave": true,
        "editor.defaultFormatter": "charliermarsh.ruff",
        "[python]": {
          "editor.defaultFormatter": "charliermarsh.ruff",
          "editor.codeActionsOnSave": {
            "source.organizeImports": "explicit",
            "source.fixAll.ruff": "explicit"
          }
        }
      },
      "extensions": [
        "charliermarsh.ruff",
        "ms-python.python",
        "ms-python.mypy-type-checker",
        "tamasfe.even-better-toml",
        "GitHub.vscode-pull-request-github",
        "eamodio.gitlens"
      ]
    }
  },
  "remoteUser": "vscode"
}
```

## Notes

- Base image uses Python 3.12 (pinned via devcontainer base image; `uv` manages the actual runtime version independently).
- `onCreateCommand` installs `uv` via pip once, then `uv sync --extra dev` installs the project and all dev dependencies.
- `postCreateCommand` installs pre-commit hooks if a `.pre-commit-config.yaml` exists (silently skips if absent).
- VS Code extensions: `charliermarsh.ruff` for format-on-save, `ms-python.mypy-type-checker` for inline type hints.
- `remoteUser: vscode` keeps permissions correct inside the container.
