---
name: apply-tdd-loop-en
description: >
  Applies the Test-Driven Development (TDD) cycle as an agentic loop of
  RED -> GREEN -> REFACTOR iterations until all requirements are covered or
  all existing code paths are tested. Use when a user or agent wants to write
  code strictly test-first, add missing tests to existing code, or drive a
  full TDD session for a module, class, or function. Activate for trigger
  phrases like: "apply TDD", "write this test-first", "do a TDD loop",
  "TDD cycle for", "drive TDD on", "red green refactor", or
  "add tests then implement".
license: CC BY-NC-SA 4.0
compatibility: Requires git. Python/pytest or Java/JUnit 5 recommended for examples.
metadata:
  author: roebi
  spec: https://agentskills.io/specification
  reference: https://en.wikipedia.org/wiki/Test-driven_development
---

# Apply TDD Loop

Drives a strict Test-Driven Development loop — RED → GREEN → REFACTOR —
as an agentic cycle. Accepts two entry points: a list of requirements
(test-first, greenfield) or existing code that needs test coverage added.
The loop runs until all requirements are covered or all code paths are tested.

## When to use this skill

- User wants to implement a feature strictly test-first
- User wants to add missing tests to existing code and refactor safely
- An orchestrating skill (e.g. `create-tested-algorithms-from-requirements-en`)
  delegates the inner TDD loop to this skill
- Trigger phrases: "apply TDD", "TDD loop", "red green refactor",
  "write test first", "drive TDD on", "add tests then implement"

---

## Entry points

### Entry Point A — Requirement-driven (greenfield)

**Input:**
- A list of requirements (user stories, acceptance criteria, or plain sentences)
- Target language and test framework
- Optional: existing scaffold or module name

**Goal:** implement each requirement exactly once, test-first.

### Entry Point B — Code-driven (coverage-first)

**Input:**
- Existing source file(s) with little or no tests
- Target language and test framework
- Optional: coverage report or list of untested paths

**Goal:** write a failing test for each untested path, make it pass,
then refactor.

> For Entry Point B, start by listing all public methods / branches
> without tests. Treat each as a mini-requirement and proceed with
> the standard loop below.

---

## The Agentic TDD Loop

```
LOOP:
  1. RED    — write ONE failing test for the next requirement / untested path
  2. GREEN  — write the minimal code to make ONLY that test pass
  3. REFACTOR — clean up code and tests without breaking anything
  4. CHECK  — are all requirements / paths covered? if YES → EXIT LOOP
              if NO  → next iteration (go to 1)
```

### Loop State

Track the following state across iterations. If the session may span
multiple turns, persist this in a `Handover-State.md` file.

```yaml
# Handover-State.md — TDD loop state
skill: apply-tdd-loop-en
entry_point: A | B          # which entry point was used
language: <e.g. Python, Java, TypeScript>
test_framework: <e.g. pytest, JUnit 5, Jest>
requirements:               # Entry Point A
  - [ ] req-1: <text>
  - [ ] req-2: <text>
untested_paths:             # Entry Point B
  - [ ] path-1: <method / branch>
  - [ ] path-2: <method / branch>
current_iteration: 1
current_phase: RED | GREEN | REFACTOR
last_test_added: <test name>
last_code_change: <brief description>
last_green_commit: <git SHA of last fully green state>
exit_condition_met: false
```

Update the state after each phase before proceeding to the next.

---

## Phase Instructions

### Phase 1 — RED

- Select the **next unchecked** requirement or untested path.
- Write **one** test that:
  - Has a clear, descriptive name (`test_<what>_<when>_<expected>`)
  - Asserts the expected behaviour defined by the requirement
  - Fails when run against current code (no implementation yet)
- Run the test. Confirm it **fails** for the right reason
  (missing implementation, not a syntax error or wrong import).
- Do NOT write any production code in this phase.
- Update loop state: `current_phase: GREEN`

### Phase 2 — GREEN

- Write the **minimal** production code to make the failing test pass.
- Minimal means: no extra logic, no anticipating future requirements.
- Run **all** tests. Confirm:
  - The new test passes
  - All previously passing tests still pass (no regression)
- If a regression occurs: fix it before moving to REFACTOR.
- **Revert rule:** if a regression is not obviously fixable within a few
  minutes, do NOT debug excessively — instead:
  ```bash
  git revert HEAD   # or: git checkout -- .
  ```
  Reset `current_phase: RED`, rethink the test or the minimal code, retry.
- Update loop state: `current_phase: REFACTOR`

### Phase 3 — REFACTOR

- Review both the new production code and the new test.
- Apply clean-code improvements: remove duplication, improve naming,
  extract helpers, simplify logic.
- Run **all** tests again after each change. Must stay green.
- Guiding principles (keep it simple):
  - DRY — Don't Repeat Yourself
  - SRP — Single Responsibility Principle
  - KISS — Keep It Simple
- Mark the current requirement / path as `[x]` in loop state.
- **Commit now** — one small, atomic commit per completed iteration:
  ```bash
  git add -A
  git commit -m "test: add test for <requirement>"   # after RED
  git commit -m "feat: implement <requirement>"       # after GREEN
  git commit -m "refactor: clean <what>"              # after REFACTOR (if changed)
  ```
  Small commits mean any future failure can be reverted instantly
  without losing other work.
- Record the new SHA in loop state: `last_green_commit: <sha>`
- Update loop state: `current_phase: RED`, increment `current_iteration`

### Exit Condition

After REFACTOR, check:

```
All items in requirements[] or untested_paths[] are marked [x]?
  YES → set exit_condition_met: true, summarise results, EXIT LOOP
  NO  → continue to next RED phase
```

---

## Use Case Examples

### Example A — Requirement-driven (Python / pytest)

**Requirements input:**
```
1. add(a, b) returns the sum of two integers
2. add(a, b) raises TypeError if either argument is not an integer
```

**Iteration 1 — RED:**
```python
# test_calculator.py
def test_add_returns_sum_of_two_integers():
    assert add(1, 2) == 3  # FAILS — add() not defined yet
```

**Iteration 1 — GREEN:**
```python
# calculator.py
def add(a, b):
    return a + b
```

**Iteration 1 — REFACTOR:** no duplication, naming is clear — nothing to change.

**Iteration 2 — RED:**
```python
def test_add_raises_type_error_for_non_integer():
    with pytest.raises(TypeError):
        add("x", 2)  # FAILS — no type check yet
```

**Iteration 2 — GREEN:**
```python
def add(a, b):
    if not isinstance(a, int) or not isinstance(b, int):
        raise TypeError("Both arguments must be integers")
    return a + b
```

**Iteration 2 — REFACTOR:** extract guard if reused elsewhere — not needed here.

All requirements covered → EXIT LOOP.

---

### Example B — Code-driven (Java / JUnit 5)

**Existing untested method:**
```java
public int divide(int a, int b) {
    return a / b;
}
```

**Untested paths identified:**
```
1. normal division: divide(10, 2) → 5
2. division by zero: divide(5, 0) → ArithmeticException
```

Proceed with the standard loop, treating each path as a requirement.

---

## Tips and Edge Cases

- **One test per iteration.** Never write multiple failing tests at once —
  it defeats the discipline of TDD.
- **Test names are documentation.** A good test name makes the requirement
  readable without opening the implementation.
- **Green must mean green.** Do not move to REFACTOR if any test is red.
- **REFACTOR is mandatory.** Skipping it accumulates technical debt.
  Even "nothing to refactor" is a valid outcome — but it must be checked.
- **Stuck on GREEN?** If minimal code is not obvious, write the simplest
  possible thing (even hardcoded), then let the next iteration force
  generalisation (triangulation).
- **Multi-session:** save `Handover-State.md` to the working directory.
  Resume by loading state and continuing from `current_phase`.
