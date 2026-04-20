---
name: create-file-tree-for-topic-en
license: CC BY-NC-SA 4.0
description: >
  Creates a topic-specific directory and file tree scaffold (Gerüst) as a
  starting point for a software solution or skill collection. Generates empty
  files, adds placeholder.txt in every empty directory so git tracks it,
  and writes a README.md in the root with metadata: topic, version, description,
  create timestamp (YYYYMMDD_HHMISS), creator, and license.
  Activate for phrases like: "create a file tree for", "scaffold a project for",
  "create directory structure for", "bootstrap a file scaffold", "Gerüst für",
  "starting point for", "create folder structure", or "new project skeleton".
metadata:
  author: roebi
  spec: https://agentskills.io/specification
  version: "0.1.0"
---

# Create File Tree for Topic

Creates a topic-specific directory and file tree scaffold as a clean starting
point for a software solution or a skill collection.

## What this skill produces

```
<topic>/
├── README.md                  ← metadata header (see format below)
├── src/
│   └── placeholder.txt        ← keeps empty dir in git
├── tests/
│   └── placeholder.txt
├── docs/
│   └── placeholder.txt
└── ...                        ← topic-specific dirs + empty files
```

All files are empty except `README.md` and `placeholder.txt` files.

---

## Step-by-step workflow

### Step 1 — Collect inputs

Ask the user for (or derive from context):

| Input | Required | Default / Fallback |
|---|---|---|
| `topic` | ✅ | — |
| `description` | ✅ | ask user |
| `version` | ✅ | `0.1.0` |
| `license` | ✅ | `MIT` for SW topics · `CC BY-NC-SA 4.0` for skill collections |
| `creator` | optional | run `git config user.name`; if empty → ask user |
| `language` | optional | `en` |

**License selection rule:**
- SW project (code, tool, library, app) → **MIT**
- Skill collection, methodology, learning content → **CC BY-NC-SA 4.0**
- When in doubt → ask the user.

### Step 2 — Brainstorm the tree

Based on the topic, propose a meaningful directory and file structure.
Apply KISS: start small. Typical patterns:

**SW project (e.g. "cli-todo-app"):**
```
<topic>/
├── README.md
├── src/
│   └── placeholder.txt
├── tests/
│   └── placeholder.txt
├── docs/
│   └── placeholder.txt
└── .gitignore               ← empty
```

**Skill collection (e.g. "stoicism-skills"):**
```
<topic>/
├── README.md
├── skills/
│   └── placeholder.txt
├── references/
│   └── placeholder.txt
└── assets/
    └── placeholder.txt
```

**Python package:**
```
<topic>/
├── README.md
├── src/
│   └── <topic>/
│       ├── __init__.py      ← empty
│       └── placeholder.txt
├── tests/
│   └── placeholder.txt
├── docs/
│   └── placeholder.txt
├── pyproject.toml           ← empty
└── .gitignore               ← empty
```

Present the proposed tree to the user as a fenced block. **Wait for
confirmation before creating any files.**

### Step 3 — Generate the timestamp

```bash
date +"%Y%m%d_%H%M%S"
# Output example: 20240324_142305
# Format: YYYYMMDD_HHMISS  (HH=hour, MI=minutes, SS=seconds)
```

Resolve creator:
```bash
CREATOR=$(git config user.name 2>/dev/null)
if [ -z "$CREATOR" ]; then
  # Ask the user: "Who should be listed as creator?"
fi
```

### Step 4 — Write README.md

Use this exact template in the root `README.md`:

```markdown
# <topic>

> <description>

## Scaffold Metadata

| Field       | Value                        |
|-------------|------------------------------|
| Topic       | <topic>                      |
| Version     | <version>                    |
| Created     | <YYYYMMDD_HHMISS>            |
| Creator     | <creator>                    |
| License     | <license>                    |
| Language    | en                           |

## Structure

\`\`\`
<paste the confirmed tree here>
\`\`\`

## Getting Started

<!-- Add setup instructions here -->

## Notes

<!-- Add any additional context here -->
```

### Step 5 — Create directories and files

For every directory in the confirmed tree:
- Create the directory.
- If the directory has **no other files** in it (i.e. only a
  `placeholder.txt` is listed), create `placeholder.txt` with this content:

```
# placeholder
# This file exists so git tracks this otherwise empty directory.
# Remove it once you add real files here.
```

For every **named empty file** in the tree (e.g. `.gitignore`,
`pyproject.toml`, `__init__.py`): create it with zero bytes.

### Step 6 — Confirm and summarise

After creating all files, print a summary:
```
✅ Scaffold created for topic: <topic>
   Root: ./<topic>/
   Files created: <N>
   Timestamp: <YYYYMMDD_HHMISS>
   Creator: <creator>
   License: <license>

Next steps:
  cd <topic>
  git init
  git add .
  git commit -m "chore: initial scaffold for <topic>"
```

---

## Rules

- **KISS**: prefer flat over deep. Max 3 levels unless the topic demands it.
- **No content**: all non-README files are empty placeholders unless the
  user explicitly requests seed content.
- **placeholder.txt only in empty dirs**: never add `placeholder.txt` next
  to real files.
- **Ask before creating**: always show the proposed tree and wait for user
  confirmation before touching the filesystem.
- **Idempotent**: if the root directory already exists, warn the user and
  stop — do not overwrite.

---

## Scripts

A helper script is available at `scripts/create-file-tree.sh` for
generating the scaffold from the command line. See that file for usage.

---

## References

- `references/tree-patterns.md` — curated tree patterns for common topic types
