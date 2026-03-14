---
name: quick-documentation-en
version: 1.0.0
license: CC BY-NC-SA 4.0
description: >
  Generates compact JSDoc comments or Python docstrings directly above function
  definitions. Activate for phrases like "doc-this", "document this",
  "add docs", "add a docstring", "add JSDoc", or whenever the user requests
  documentation for a code block. Supports JavaScript, TypeScript, and Python.
  Does not alter any code logic.
metadata:
  author: roebi
  spec: https://agentskills.io/specification
  lang: en
  instruction-language: en
  encoding: utf-8
---

# Quick Documentation

Creates precise inline documentation for the highlighted or following code block.
No lengthy explanations outside the code — just clean, concise docstrings placed
directly above the function.

## When to use this skill

| Trigger phrase       | Context                                          |
|----------------------|--------------------------------------------------|
| `doc-this`           | Cursor is on a function                          |
| `document this`      | User highlights a code block                     |
| `add docs`           | New function with no documentation present       |
| `add a docstring`    | Existing function, docstring is missing          |
| `add JSDoc`          | JavaScript or TypeScript file                    |

## Step-by-Step Instructions

### 1. Identify the programming language

- Check the file extension or syntax hints (`.js`, `.ts` → JSDoc; `.py` → PEP 257).
- If unclear, ask briefly.

### 2. Analyse the function

- **Parameters**: name, type, whether optional.
- **Return value**: type and semantic meaning.
- **Exceptions / errors**: known throws or raises.
- **Short description**: what the function does — not how.

### 3. Write the docstring

**JavaScript / TypeScript — JSDoc:**

```js
/**
 * Calculates the total price including VAT.
 *
 * @param {number} net  - Net price in CHF.
 * @param {number} vat  - VAT rate as a decimal (e.g. 0.077).
 * @returns {number} Gross price in CHF.
 * @throws {RangeError} If `vat` is negative.
 */
function calculateGross(net, vat) { ... }
```

**Python — PEP 257 (Google style):**

```python
def calculate_gross(net: float, vat: float) -> float:
    """Calculates the total price including VAT.

    Args:
        net: Net price in CHF.
        vat: VAT rate as a decimal (e.g. 0.077).

    Returns:
        Gross price in CHF.

    Raises:
        ValueError: If `vat` is negative.
    """
```

### 4. Output

- Insert the docstring **directly above** the function definition.
- Return the rest of the code unchanged.
- No additional explanations outside the code block.

## Constraints

- Do not write lengthy explanations outside the code.
- Do **not** alter any code logic.
- Use concise, technical language.
- Follow the relevant standard: JSDoc for JS/TS, PEP 257 for Python.

## Reference files in this skill

- `references/example.py` — Python example: single-line docstring for a helper function
