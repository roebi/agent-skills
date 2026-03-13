# Publish Workflow Template (Trusted Publishing / OIDC)

File: `.github/workflows/publish.yml`

No API tokens needed. Uses PyPI's OIDC Trusted Publishing — see Phase 8 of the skill for the PyPI configuration steps.

```yaml
name: Publish to PyPI

on:
  push:
    tags:
      - "v*"

permissions:
  contents: read

jobs:
  build:
    name: Build distribution
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
        with:
          enable-cache: true
      - name: Build wheel and sdist
        run: uv build
      - name: Upload dist artifacts
        uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/

  publish:
    name: Publish to PyPI
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: pypi
      url: https://pypi.org/p/PROJECT_NAME
    permissions:
      id-token: write   # required for OIDC Trusted Publishing
    steps:
      - name: Download dist artifacts
        uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
```

## Notes

- The `environment: pypi` block links this workflow to the GitHub Environment named `pypi`. This is the exact name you must register in PyPI's Trusted Publishing UI.
- The `id-token: write` permission is what enables OIDC — no `PYPI_TOKEN` secret needed.
- Separating `build` and `publish` into two jobs means the build artifact is inspectable before publishing.
- Tag format: push `v0.1.0` (not `0.1.0`) — the `v*` pattern requires the prefix.
- To publish to TestPyPI first, duplicate the `publish` job pointing to `https://test.pypi.org/legacy/` using `repository-url` on the `pypa/gh-action-pypi-publish` action.
