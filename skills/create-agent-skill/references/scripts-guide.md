# Scripts Guide for Agent Skills

Reference: [agentskills.io/skill-creation/using-scripts](https://agentskills.io/skill-creation/using-scripts)

## When to use a script vs inline instructions

Use a **script** when:
- The same command sequence runs repeatedly
- A command grows too complex to get right on the first attempt inline
- The task requires structured output that other tools will parse
- The operation is destructive and needs a `--dry-run` safeguard

Use **inline instructions** (one-off commands) when:
- An existing package already does the job with a few flags
- The command is simple enough to be reliable inline

## One-off commands — prefer versioned runners

```bash
# Python tools — uvx (recommended) or pipx
uvx ruff@0.8.0 check .
pipx run 'black==24.10.0' .

# Node tools — npx
npx eslint@9 --fix .

# Go tools
go run github.com/golangci/golangci-lint/cmd/golangci-lint@v1.62.0 run
```

Always pin versions for reproducibility.

## Self-contained Python script (PEP 723)

```python
#!/usr/bin/env python3
# /// script
# dependencies = [
#   "requests>=2.32,<3",
#   "rich>=13,<14",
# ]
# requires-python = ">=3.11"
# ///
"""
Brief description of what this script does.

Usage: scripts/myscript.py [OPTIONS] INPUT
"""

import argparse
import json
import sys


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input", help="Input value or file path")
    parser.add_argument("--format", choices=["json", "text"], default="json",
                        help="Output format (default: json)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would happen without making changes")
    args = parser.parse_args()

    result = {"input": args.input, "dry_run": args.dry_run}

    if args.format == "json":
        print(json.dumps(result))
    else:
        print(f"Input: {args.input}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

Run with: `uv run scripts/myscript.py --help`

## Critical rules for agentic scripts

### No interactive prompts — ever

```python
# BAD — hangs forever in an agent shell
target = input("Enter target: ")

# GOOD — clear error with usage hint
if not args.target:
    print("Error: --target is required. Options: dev, staging, prod.", file=sys.stderr)
    print("Usage: scripts/deploy.py --target staging --version v1.2.3", file=sys.stderr)
    sys.exit(1)
```

### stdout = data, stderr = diagnostics

```python
import sys

# Structured output the agent can parse
print(json.dumps(result))

# Progress, warnings, debug info go to stderr
print("Processing 42 items...", file=sys.stderr)
print(f"Warning: skipped {skipped} items", file=sys.stderr)
```

### Meaningful exit codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | User error (bad args, missing required input) |
| 2 | System/environment error (missing dependency, network failure) |
| 3+ | Domain-specific errors — document in `--help` |

### Output size control

Agents truncate large outputs (typically at 10–30K chars). Always:
- Default to a summary or reasonable row limit
- Support `--limit N` and `--offset N` for pagination
- Or require `--output FILE` for large outputs

```python
parser.add_argument("--limit", type=int, default=50,
                    help="Max items to return (default: 50)")
parser.add_argument("--output", default="-",
                    help="Output file path, or - for stdout (default: -)")
```

### Idempotency

Agents retry commands. Design scripts so running them twice is safe:

```python
# BAD — fails on second run
os.mkdir(output_dir)

# GOOD — safe to retry
os.makedirs(output_dir, exist_ok=True)
```

### Dry-run for destructive operations

```python
if args.dry_run:
    print(json.dumps({"action": "would_delete", "path": str(path), "dry_run": True}))
else:
    path.unlink()
    print(json.dumps({"action": "deleted", "path": str(path)}))
```

## Shell scripts

```bash
#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat << EOF
Usage: $(basename "$0") [OPTIONS] INPUT

Brief description.

Options:
  --dry-run    Show what would happen without making changes
  --format     Output format: json|text (default: json)
  -h, --help   Show this help

Exit codes:
  0  Success
  1  Usage error
  2  Runtime error
EOF
}

DRY_RUN=false
FORMAT=json

while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run) DRY_RUN=true; shift ;;
    --format)  FORMAT="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *)         INPUT="$1"; shift ;;
  esac
done

if [[ -z "${INPUT:-}" ]]; then
  echo "Error: INPUT is required." >&2
  usage >&2
  exit 1
fi

echo "{\"input\": \"$INPUT\", \"dry_run\": $DRY_RUN}"
```
