#!/usr/bin/env bash
# create-file-tree.sh — scaffold a topic directory + file tree
#
# Usage:
#   bash create-file-tree.sh --topic <topic> --description "<desc>" \
#       [--version 0.1.0] [--license MIT] [--creator "Name"] [--dry-run]
#
# Exit codes: 0=success  1=user error  2=system error

set -euo pipefail

# ── defaults ────────────────────────────────────────────────────────────────
TOPIC=""
DESCRIPTION=""
VERSION="0.1.0"
LICENSE="MIT"
CREATOR=""
DRY_RUN=false
LANGUAGE="en"

# ── help ─────────────────────────────────────────────────────────────────────
usage() {
  cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Scaffold a topic-specific directory and file tree as a project starting point.

Options:
  --topic        TOPIC        Topic / project name (required, becomes root dir)
  --description  DESC         One-liner description (required)
  --version      VERSION      Version string (default: 0.1.0)
  --license      LICENSE      License identifier (default: MIT)
                              Use 'CC BY-NC-SA 4.0' for skill collections
  --creator      CREATOR      Creator name (default: git config user.name)
  --language     LANG         Language tag (default: en)
  --dry-run                   Print what would be created, do not touch fs
  --help                      Show this help

Examples:
  bash create-file-tree.sh --topic cli-todo-app --description "A CLI todo app in Python"
  bash create-file-tree.sh --topic stoicism-skills --description "Stoicism agent skills" \\
      --license "CC BY-NC-SA 4.0" --dry-run
EOF
}

# ── argument parsing ──────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --topic)       TOPIC="$2";       shift 2 ;;
    --description) DESCRIPTION="$2"; shift 2 ;;
    --version)     VERSION="$2";     shift 2 ;;
    --license)     LICENSE="$2";     shift 2 ;;
    --creator)     CREATOR="$2";     shift 2 ;;
    --language)    LANGUAGE="$2";    shift 2 ;;
    --dry-run)     DRY_RUN=true;     shift   ;;
    --help|-h)     usage; exit 0     ;;
    *) echo "❌ Unknown option: $1" >&2; usage; exit 1 ;;
  esac
done

# ── validation ────────────────────────────────────────────────────────────────
if [[ -z "$TOPIC" ]]; then
  echo "❌ --topic is required." >&2; exit 1
fi
if [[ -z "$DESCRIPTION" ]]; then
  echo "❌ --description is required." >&2; exit 1
fi
if [[ -d "$TOPIC" ]]; then
  echo "❌ Directory '$TOPIC' already exists. Aborting to avoid overwrite." >&2; exit 1
fi

# ── resolve creator ───────────────────────────────────────────────────────────
if [[ -z "$CREATOR" ]]; then
  CREATOR=$(git config user.name 2>/dev/null || true)
fi
if [[ -z "$CREATOR" ]]; then
  echo "❌ Could not determine creator. Pass --creator 'Your Name'." >&2; exit 1
fi

# ── timestamp YYYYMMDD_HHMISS ──────────────────────────────────────────────────
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# ── tree definition ───────────────────────────────────────────────────────────
# Directories that will receive a placeholder.txt (empty dirs)
EMPTY_DIRS=(
  "$TOPIC/src"
  "$TOPIC/tests"
  "$TOPIC/docs"
)
# Files that will be created empty (non-placeholder)
EMPTY_FILES=(
  "$TOPIC/.gitignore"
)

# ── helper functions ──────────────────────────────────────────────────────────
PLACEHOLDER_CONTENT='# placeholder
# This file exists so git tracks this otherwise empty directory.
# Remove it once you add real files here.'

make_dir() {
  if $DRY_RUN; then
    echo "  [dry] mkdir -p $1"
  else
    mkdir -p "$1"
  fi
}

make_placeholder() {
  local dir="$1"
  local target="$dir/placeholder.txt"
  if $DRY_RUN; then
    echo "  [dry] create $target"
  else
    printf '%s\n' "$PLACEHOLDER_CONTENT" > "$target"
  fi
}

make_empty_file() {
  if $DRY_RUN; then
    echo "  [dry] touch $1"
  else
    touch "$1"
  fi
}

# ── README.md content ─────────────────────────────────────────────────────────
readme_content() {
cat <<README
# ${TOPIC}

> ${DESCRIPTION}

## Scaffold Metadata

| Field       | Value                        |
|-------------|------------------------------|
| Topic       | ${TOPIC}                     |
| Version     | ${VERSION}                   |
| Created     | ${TIMESTAMP}                 |
| Creator     | ${CREATOR}                   |
| License     | ${LICENSE}                   |
| Language    | ${LANGUAGE}                  |

## Structure

\`\`\`
${TOPIC}/
├── README.md
├── src/
│   └── placeholder.txt
├── tests/
│   └── placeholder.txt
├── docs/
│   └── placeholder.txt
└── .gitignore
\`\`\`

## Getting Started

<!-- Add setup instructions here -->

## Notes

<!-- Add any additional context here -->
README
}

# ── build ─────────────────────────────────────────────────────────────────────
echo "🌲 Scaffolding file tree for topic: ${TOPIC}"
echo "   Timestamp : ${TIMESTAMP}"
echo "   Creator   : ${CREATOR}"
echo "   License   : ${LICENSE}"
$DRY_RUN && echo "   Mode      : DRY RUN — no files will be created"
echo ""

# root dir
make_dir "$TOPIC"

# README.md
if $DRY_RUN; then
  echo "  [dry] create ${TOPIC}/README.md"
else
  readme_content > "${TOPIC}/README.md"
fi

# empty dirs with placeholder
for dir in "${EMPTY_DIRS[@]}"; do
  make_dir "$dir"
  make_placeholder "$dir"
done

# named empty files
for f in "${EMPTY_FILES[@]}"; do
  make_empty_file "$f"
done

# ── summary ───────────────────────────────────────────────────────────────────
echo ""
if $DRY_RUN; then
  echo "✅ Dry run complete. No files were written."
else
  FILE_COUNT=$(find "$TOPIC" -type f | wc -l)
  echo "✅ Scaffold created for topic: ${TOPIC}"
  echo "   Root        : ./${TOPIC}/"
  echo "   Files created: ${FILE_COUNT}"
  echo ""
  echo "Next steps:"
  echo "  cd ${TOPIC}"
  echo "  git init"
  echo "  git add ."
  echo "  git commit -m \"chore: initial scaffold for ${TOPIC}\""
fi
