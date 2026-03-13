# Toolchain Rationale

Why each tool was chosen for this skill. Reference this when a user asks "why X instead of Y".

---

## uv (env/dep management frontend)

**Chosen over**: `hatch` (env frontend), `poetry`, `pip+venv`

`uv` is written in Rust and is 10–100× faster than pip for installs and lockfile generation. It provides a single binary with no Python dependency for bootstrapping, which simplifies both CI and devcontainer setup. The JetBrains Python Developer Survey 2024 showed uv reaching 11% adoption in its first year — the fastest ramp of any Python tooling addition in recent survey history. By early 2026 uv surpassed Poetry in monthly PyPI downloads (~75M vs ~66M). Its `uv init`, `uv add`, `uv build`, and `uv publish` commands cover the full project lifecycle. The main risk is Astral's VC backing without a clear monetisation path; however the tool is open-source (MIT) and the Python community has indicated it would fork/maintain if needed.

`hatch` remains excellent and is officially PyPA-blessed, but its frontend UX is more opinionated and its install speed is not competitive with uv. We keep `hatchling` as the **build backend** (see below) because it has features uv_build does not yet match.

---

## hatchling (build backend)

**Chosen over**: `uv_build`, `flit-core`, `setuptools`

`hatchling` is mature, PyPA-blessed, and supports VCS-based dynamic versioning via `hatch-vcs` (version derived from git tags — no manual `__version__` bumps). It has fine-grained file inclusion patterns and supports custom build hooks. `uv_build` is the natural backend if using uv as frontend, but as of 2025/2026 it does not yet support VCS versioning or hooks. We use `hatchling` as the backend and `uv` as the frontend — this is the community-recommended hybrid for non-trivial packages.

---

## ruff (linter + formatter)

**Kept from aider-skills baseline.**

Replaces `black`, `isort`, and `flake8` with a single Rust-based tool. The JetBrains 2024 survey showed ruff adoption rising to 35% (up from 20% in 2023), second only to black. It is 10–100× faster and the selected rule set (`E`, `W`, `F`, `I`, `B`, `UP`, `C4`, `SIM`) covers everything the three legacy tools did. Configure once in `pyproject.toml`, no separate config files needed.

---

## pytest (test runner)

**Kept from aider-skills baseline.**

67% adoption in the JetBrains 2024 survey, far ahead of any alternative. `pytest-cov` adds coverage reporting with zero friction. No alternative considered — pytest is the de-facto standard.

---

## mypy (type checker, opt-in)

**Chosen over**: `pyright`

`mypy` has 67% adoption vs pyright's 38% per the 2024 Python typing survey. Its plugin ecosystem handles dynamic patterns (SQLAlchemy, Django models, dataclasses) that pyright struggles with. We configure it as **non-blocking** in CI (`continue-on-error: true`) — type errors are surfaced as warnings, not merge blockers. This gives type-safety feedback without stalling the development loop.

`pyright` is excellent and 3–5× faster, but requires Node.js to run standalone (awkward in Python-first CI). It is included automatically via VS Code's Pylance extension in the devcontainer, giving developers inline type hints in the IDE regardless of the CI choice.

**Future watch**: Astral's `ty` (Rust-based) and Meta's `pyrefly` are both targeting this space. Revisit this choice in 2026/2027.

---

## GitHub Actions + Trusted Publishing

**Kept from aider-skills baseline.**

Trusted Publishing (OIDC) eliminates long-lived API tokens from GitHub secrets entirely. The PyPA-recommended approach since 2023; supported by PyPI since May 2023. The `pypa/gh-action-pypi-publish` action handles the token exchange transparently.

---

## Source (`src/`) layout

PEP 517 best practice. Prevents Python from accidentally importing the package from the repo root during development (before installation), which would bypass `__init__.py` logic and mask import errors. All major packaging guides (PyPA, Hatch, uv) recommend `src/` layout as of 2024.
