---
name: terminal-cli
description: >
  Reference for operating in a Linux terminal. Use when the user or agent needs
  to run bash commands, combine commands with && or pipes, read files, sort and
  deduplicate output, write and execute shell scripts, work with the filesystem
  (files, links, mounts, permissions), install or update packages, get help on
  commands, manage containers with Podman, make HTTP requests with curl, manage
  Kubernetes clusters with kubectl, manage Helm charts, handle environment
  variables, or launch AI coding agents (aider-chat, claude). Activate this
  skill for any task involving: bash, shell, terminal, CLI, script, pipe,
  podman, kubectl, helm, curl, apt, pip, environment variable, aider, or any
  Unix command.
compatibility: Requires a Linux (bash) environment.
---

# Terminal & CLI Skill

Reference for working in a Linux terminal — covering the full stack from basic
bash to container orchestration and AI agent execution.

## How to use this skill

This file covers the most common patterns. For detailed command references,
load the relevant file from `references/` on demand:

| Topic | Reference file |
|-------|---------------|
| Bash core: pipes, scripts, filesystem, install, env vars | `references/bash.md` |
| Containers: Podman, Kubernetes (kubectl), Helm | `references/containers.md` |
| HTTP requests: curl | `references/curl.md` |
| AI agents: aider-chat, claude CLI | `references/agents.md` |

---

## 1. Run a bash command

```bash
command [options] [arguments]

# Run sequentially — stop on first failure
cmd1 && cmd2 && cmd3

# Run regardless of failure
cmd1; cmd2; cmd3

# Capture output into a variable
OUTPUT=$(command)

# Redirect stdout / stderr / both
command > out.txt
command 2> err.txt
command &> all.txt

# Discard all output
command > /dev/null 2>&1
```

## 2. Check if a tool exists

```bash
type -a tool_name      # All locations where tool is found
apropos keyword        # Find commands matching a keyword
which tool_name        # First binary on PATH
whereis tool_name      # Binary, source, and man page locations
```

## 3. Combine with &&

```bash
# Only proceed if previous command succeeded
sudo apt update && sudo apt upgrade -y

# Chain multiple steps safely
mkdir -p build && cd build && cmake ..
```

## 4. Pipe with |

```bash
# Pass stdout of one command as stdin to the next
cmd1 | cmd2 | cmd3

# Common patterns
ls -la | grep ".conf"
ps aux | grep nginx
journalctl -u myservice | grep ERROR | tail -20
cat file.txt | wc -l
```

## 5. Read content with cat

```bash
cat file.txt                   # Full file to stdout
cat file1.txt file2.txt        # Concatenate multiple files
head -n 20 file.txt            # First 20 lines
tail -n 20 file.txt            # Last 20 lines
tail -f /var/log/app.log       # Follow live log output
less file.txt                  # Paginated view (q to quit)
grep "pattern" file.txt        # Lines matching pattern
grep -r "pattern" ./dir/       # Recursive search in directory
grep -n "pattern" file.txt     # With line numbers
grep -i "pattern" file.txt     # Case-insensitive
```

## 6. Sort results

```bash
sort file.txt                  # Alphabetical (ascending)
sort -r file.txt               # Reverse order
sort -n file.txt               # Numeric sort
sort -k2 file.txt              # Sort by column 2
sort -t: -k3 -n /etc/passwd    # Custom delimiter (:), column 3, numeric
ls -la | sort -k5 -n           # Sort ls output by file size (col 5)
```

## 7. Unique results

```bash
# uniq only removes *consecutive* duplicates — always sort first
sort file.txt | uniq            # Deduplicate
sort file.txt | uniq -c        # Count occurrences
sort file.txt | uniq -d        # Show only duplicates
sort file.txt | uniq -u        # Show only lines that appear once

# Typical pipeline: count error types in a log
cat app.log | grep ERROR | sort | uniq -c | sort -rn
```

## 8. Write and run scripts with heredoc

```bash
# Create a script file inline
cat << 'EOF' > myscript.sh
#!/bin/bash
set -euo pipefail   # Exit on error, unset var, or pipe failure

echo "Today: $(date +%Y-%m-%d)"

for i in 1 2 3; do
  echo "Step $i"
done
EOF

chmod +x myscript.sh
./myscript.sh

# Or run directly without creating a file
bash << 'EOF'
echo "Inline execution"
ls -la /tmp
EOF
```

**Script best practices:**
- Always start with `#!/bin/bash`
- Use `set -euo pipefail` for safe defaults
- Always quote variables: `"$VAR"` not `$VAR`
- Use `$(...)` instead of backticks

## 9. Filesystem — quick reference

```bash
# Navigate & inspect
pwd && ls -lah              # Where am I + what's here
tree -L 2                   # Directory tree (2 levels deep)
find /path -name "*.log"    # Find by name
du -sh /path                # Size of a directory
df -h                       # Disk usage of all mounts

# Create / copy / move / delete
mkdir -p /path/to/dir       # Create with parents
cp -r src/ dst/             # Copy directory
mv src dst                  # Move or rename
rm -rf dir/                 # Delete recursively (irreversible)

# Permissions & ownership
chmod +x file               # Make executable
chmod 644 file              # rw-r--r--
chown user:group file       # Change owner

# Links
ln -s /target /link         # Symbolic link
readlink -f /link           # Resolve symlink to real path

# Mounts
mount                       # List all active mounts
lsblk                       # Block device tree
findmnt                     # Mount point tree
```

→ Full filesystem reference: `references/bash.md`

## 10. Install & update — quick reference

```bash
# APT
sudo apt update && sudo apt upgrade -y
sudo apt install -y package-name

# pip (Python)
pip install package --break-system-packages

# npm (Node.js)
npm install -g package-name
```

→ Full install reference (snap, from-source, pip options): `references/bash.md`

## 11. Get help on a command

```bash
command --help              # Inline help (fastest)
man command                 # Full manual page
apropos keyword             # Search man page summaries
whatis command              # One-line description
info command                # GNU info pages (for GNU tools)
help cd                     # Help for shell builtins
```

## 12. Environment variables — quick reference

```bash
export VAR="value"          # Set for current shell and subprocesses
echo $VAR                   # Read a variable
unset VAR                   # Remove a variable
env                         # List all environment variables
VAR=value command           # Set only for a single command
```

→ Persisting vars, loading .env files: `references/bash.md`

---

## Detailed references

Load these files when you need complete command coverage:

- **`references/bash.md`** — full filesystem, install/update, env vars, scripting patterns
- **`references/containers.md`** — Podman, kubectl, Helm
- **`references/curl.md`** — curl for HTTP requests
- **`references/agents.md`** — aider-chat and claude CLI
