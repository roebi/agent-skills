---
name: create-agent-skill
description: >
  Creates a new Agent Skill that follows the agentskills.io open specification.
  Use this skill whenever a user or agent wants to author a new skill, scaffold
  a skill directory, write a SKILL.md, add reference files, or add scripts to
  an existing skill. Activate for phrases like: "create a skill", "write a
  skill", "new skill for X", "scaffold a skill", "add a skill to my repo",
  or "make a SKILL.md".
compatibility: Requires bash, git. Python optional (for skills-ref validator).
metadata:
  author: roebi
  spec: https://agentskills.io/specification
---

# Create Agent Skill

Guides you through authoring a new Agent Skill that complies with the
[agentskills.io specification](https://agentskills.io/specification).

## Specification constraints (must follow exactly)

| Field         | Rule |
|---------------|------|
| `name`        | 1–64 chars. Lowercase `a-z`, digits, hyphens only. No leading/trailing/consecutive hyphens. Must match directory name. |
| `description` | 1–1024 chars. Describes what the skill does AND when to activate it. |
| `license`     | Optional. Short license name or reference to bundled `LICENSE.txt`. |
| `compatibility` | Optional, max 500 chars. List environment requirements only if non-obvious. |
| `metadata`    | Optional. Arbitrary key-value string map. |
| `allowed-tools` | Optional, experimental. Space-delimited list of pre-approved tools. |

The `SKILL.md` body has **no format restrictions** — write whatever helps
agents perform the task. Keep it under 500 lines; move detail to `references/`.

## Directory layout

```
<skill-name>/
├── SKILL.md            # Required
├── references/         # Optional — load on demand, keep files focused
├── scripts/            # Optional — executable code (see scripts guide)
└── assets/             # Optional — templates, static files
```

## Step-by-step workflow

### 1. Gather intent

Before writing anything, clarify:

- **What does this skill do?** One clear sentence.
- **When should an agent activate it?** List trigger phrases and contexts.
- **What is the expected output?** File, command, explanation, ...
- **Are there environment dependencies?** Binaries, network access, credentials?
- **Should there be scripts?** If tasks are repetitive or complex, yes.

### 2. Choose the skill name

```bash
# Name must match the directory you will create
# Good names: pdf-processing, git-workflow, terminal-cli, code-review
# Bad: PDFProcessing, pdf_processing, -pdf, pdf--processing
```

### 3. Create the directory

```bash
mkdir -p skills/<skill-name>/references
mkdir -p skills/<skill-name>/scripts   # only if scripts are needed
```

### 4. Write SKILL.md

Start with the frontmatter, then the body:

```markdown
---
name: <skill-name>
description: >
  One paragraph. First sentence: what it does.
  Remaining sentences: when to activate it, what trigger
  phrases should cause an agent to load this skill.
---

# <Title>

Brief intro paragraph.

## When to use this skill
...

## Step-by-step instructions
...

## Examples
...
```

**Description writing guide:**

- Include both *what* (capabilities) and *when* (trigger contexts).
- List specific keywords agents can match: tool names, file types, verbs.
- Be specific enough that the agent activates this skill and not a generic fallback.
- Bad: `"Helps with PDFs."` — too vague, no trigger signals.
- Good: `"Extracts text and tables from PDF files, fills forms, merges documents. Use when the user mentions PDFs, forms, or document extraction."` — clear capability + trigger.

### 5. Add reference files (if SKILL.md would exceed 500 lines)

```bash
# Create focused reference files — one topic per file
cat > skills/<skill-name>/references/advanced.md << 'EOF'
# Advanced <Topic> Reference
...
EOF
```

Reference them from SKILL.md:

```markdown
For complete options, see `references/advanced.md`.
```

### 6. Add scripts (if needed)

See `references/scripts-guide.md` for full script design rules.

Quick rules:
- No interactive prompts — accept all input via flags or env vars.
- Always implement `--help`.
- Send structured data (JSON/CSV) to stdout, diagnostics to stderr.
- Support `--dry-run` for destructive operations.
- Use exit codes meaningfully (0 = success, 1 = user error, 2 = system error).

### 7. Validate

```bash
# Install the reference validator
pip install skills-ref --break-system-packages

# Validate your skill
skills-ref validate ./skills/<skill-name>

# Preview the XML that agents will see in their context
skills-ref to-prompt ./skills/<skill-name>
```

### 8. Add GitHub topic

After pushing your repo, add the `agent-skills` topic so others can discover
your skill at `https://github.com/topics/agent-skills`.

## Progressive disclosure reminder

An agent loads your skill in three stages:

1. **Startup** — only `name` + `description` (~100 tokens). Make the description do its job.
2. **Activation** — full `SKILL.md` body. Keep under 500 lines.
3. **On demand** — `references/` and `scripts/` files, only when the agent needs them.

Never put everything in `SKILL.md`. If you are approaching 500 lines, split.

## Reference files in this skill

- `references/scripts-guide.md` — detailed guide for writing agentic scripts
- `references/examples.md` — annotated example skills (good and bad)
