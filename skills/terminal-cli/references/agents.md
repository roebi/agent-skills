# AI Agents Reference

## aider-chat

aider is an AI pair programmer that works inside your terminal and git repository.
It edits files directly and commits changes.

### Install

```bash
pip install aider-chat --break-system-packages
```

### API keys (set before running)

```bash
export ANTHROPIC_API_KEY=sk-ant-...
export OPENAI_API_KEY=sk-...          # If using OpenAI models
```

### Start a session

```bash
cd /path/to/repo            # aider works inside a git repository
aider                       # Interactive mode, auto-selects model
aider --model claude-opus-4-5         # Use a specific model
aider --model gpt-4o
```

### Add files to context

```bash
aider file1.py file2.py     # Start with specific files in context
aider src/                  # Add a directory
```

### One-shot (non-interactive)

```bash
aider --message "add input validation to login()" auth.py
aider --message "write unit tests" --yes src/utils.py   # Auto-confirm changes
```

### Common flags

```bash
--model MODEL               # Model to use
--message "MSG"             # One-shot message, then exit
--yes                       # Auto-confirm all file changes
--no-auto-commits           # Make edits but don't commit
--dry-run                   # Show what would change, don't apply
--read file.txt             # Add read-only context file
--map-tokens 2048           # Repo map size (larger = more context)
--no-git                    # Work outside a git repo
```

### Inside an aider session

```
/add file.py          # Add file to context
/drop file.py         # Remove file from context
/files                # Show files in context
/diff                 # Show uncommitted changes
/undo                 # Undo last commit
/clear                # Clear conversation history
/exit                 # Quit aider
```

---

## claude (Claude Code CLI)

claude is Anthropic's official agentic coding CLI — it can read, write, and execute
code autonomously across an entire codebase.

### Install

```bash
npm install -g @anthropic-ai/claude-code
```

### API key

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

### Start a session

```bash
claude                         # Interactive REPL in current directory
claude --cwd /path/to/project  # Point at a specific project
```

### One-shot (non-interactive)

```bash
claude -p "explain the architecture of this codebase"
claude -p "find all TODO comments and summarize them"

# Pipe input
echo "what does this function do?" | claude -p

# Pipe file content
cat src/main.py | claude -p "review this for security issues"
```

### Common flags

```bash
-p "PROMPT"            # One-shot prompt, print result, exit
--cwd PATH             # Working directory (default: current dir)
--model MODEL          # Model to use (e.g. claude-opus-4-5)
--output-format json   # Output as JSON (for scripting)
--no-stream            # Wait for full response before printing
--allowedTools TOOLS   # Restrict which tools claude can use
--disallowedTools TOOLS
```

### Use in scripts

```bash
# Capture output
REVIEW=$(claude -p "review this PR diff" < diff.patch)
echo "$REVIEW"

# JSON output for parsing
claude -p "list all exported functions" --output-format json | jq '.result'
```

### Comparison: aider vs claude

| | aider-chat | claude CLI |
|---|---|---|
| Primary focus | Code editing + git commits | Agentic tasks across codebase |
| Works best for | Targeted file edits | Exploration, analysis, complex tasks |
| Git integration | Deep (auto-commits) | Available as a tool |
| Non-interactive | `--message` flag | `-p` flag |
| Install | pip | npm |
