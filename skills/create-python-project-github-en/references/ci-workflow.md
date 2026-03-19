# CI Workflow Template

File: `.github/workflows/ci.yml`
Replace `PYTHON_MIN` with the minimum Python version (default: `"3.12"`).

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
        with:
          enable-cache: true
      - name: Install dev dependencies
        run: uv sync --extra dev
      - name: Ruff check
        run: uv run ruff check .
      - name: Ruff format check
        run: uv run ruff format --check .
  typecheck:
    name: Type check
    runs-on: ubuntu-latest
    # mypy is informational — never block merge on type errors
    continue-on-error: true
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
        with:
          enable-cache: true
      - name: Install dev dependencies
        run: uv sync --extra dev
      - name: mypy
        run: uv run mypy src/
  test:
    name: Test / Python ${{ matrix.python-version }}
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version:
          - "PYTHON_MIN"
          - "3.12"
          - "3.13"
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
        with:
          python-version: ${{ matrix.python-version }}
          enable-cache: true
      - name: Install dev dependencies
        run: uv sync --extra dev
      - name: Run tests
        run: uv run pytest --cov=src --cov-report=term-missing
```

## Notes

- Uses `astral-sh/setup-uv@v5` — installs `uv` and optionally pins Python. Enables the uv cache for fast repeated CI runs.
- `lint` job runs `ruff check` and `ruff format --check` **before** tests — fail fast on style issues without burning test matrix minutes.
- `typecheck` job uses `continue-on-error: true` — type errors are surfaced as warnings, not CI blockers, keeping the development loop fast.
- Matrix covers `PYTHON_MIN`, `3.12`, and `3.13`. Default `PYTHON_MIN` is `3.12`. If the project supports `3.11`, add it explicitly as the first entry.
- `--cov=src` scopes coverage to the source package, avoiding test files polluting coverage stats.
