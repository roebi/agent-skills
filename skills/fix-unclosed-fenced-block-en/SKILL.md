---
name: fix-unclosed-fenced-block-en
version: 1.0.0
description: >
  Detect and fix unclosed fenced blocks (``` ... ```) in Markdown text. Use
  this skill whenever the user reports that a fenced block was not closed, when
  generated Markdown contains an unclosed fence, or when a heading or new
  section appears inside what should have been a fenced block. Fenced blocks
  are used for code, terminal output, file trees, config files, examples, and
  any verbatim content. Triggers on phrases like "unclosed fenced block",
  "missing closing fence", "backtick block not closed", or when the user pastes
  broken Markdown output for repair. Apply proactively when reviewing any
  self-generated Markdown before delivering it to the user.
license: CC BY-NC-SA 4.0
language: en
author: roebi (Robert Halter)
attribution: >
  Part of the roebi agent-skills library.
  https://github.com/roebi/agent-skills
spec: https://agentskills.io/specification
---

# fix-unclosed-fenced-block-en

Detect and fix unclosed fenced blocks (` ``` `) in Markdown output.
Fenced blocks are used for code, terminal output, file trees, config files,
examples, and any verbatim content.

---

## Problem description

When an AI assistant generates Markdown, it sometimes opens a fenced code
block with ` ``` ` (optionally followed by a language hint such as `bash` or
`markdown`) but then omits the matching closing ` ``` `.  
The symptom is that the next heading or section renders **inside** the code
block instead of as normal Markdown.

**Typical broken pattern:**

```
Some prose text.

```bash
skills-ref validate ./skills/my-skill

## Next heading        <-- should be outside the code block, but is not
```

---

## Detection algorithm

Scan the Markdown text **line by line** and maintain a simple toggle:

| State | Trigger | Action |
|-------|---------|--------|
| OUTSIDE | Line matches `` /^```/ `` | Switch to INSIDE, record line number and language hint |
| INSIDE  | Line matches `` /^```\s*$/ `` (closing fence) | Switch to OUTSIDE |
| INSIDE  | Line matches `^#{1,6} ` (ATX heading) | **Missing close detected** — insert ` ``` ` before the heading |
| INSIDE  | End of document reached | **Missing close detected** — append ` ``` ` at end |

> A closing fence must be **exactly** three or more backticks on their own
> line (optional trailing whitespace).  A line that starts with ` ``` ` but
> has additional non-whitespace characters is an **opening** fence.

---

## Fix procedure

### Step 1 — Identify all unclosed blocks

Apply the detection algorithm above to the full input text and collect every
location where a closing fence is missing.

### Step 2 — Insert closing fences

For each missing close (in reverse order so line numbers stay valid):

1. Insert a line containing exactly ` ``` ` immediately **before** the
   triggering heading (or at the end of the document).
2. Add a blank line after the inserted fence if one is not already present,
   to preserve heading spacing.

### Step 3 — Verify the result

Re-run the detection algorithm on the repaired text and confirm that no
unclosed blocks remain.

### Step 4 — Report

Tell the user:
- How many unclosed blocks were found and fixed.
- The approximate location of each fix (heading text or "end of document").

---

## Self-check before output

Before delivering **any** Markdown response, mentally (or literally) run the
detection algorithm on your own output.  If an unclosed block is found,
apply the fix before sending.

Checklist:
- [ ] Every ` ``` ` opener has a matching ` ``` ` closer on its own line.
- [ ] No ATX heading (`#` … `######`) appears between an opener and its closer.
- [ ] The document does not end while inside a fenced block.

---

## Examples

### Example 1 — heading triggers missing close

**Input (broken):**

```markdown
Preserve language hints:
```bash
skills-ref validate ./skills/my-skill

## Citations
```

**Fixed output:**

```markdown
Preserve language hints:
```bash
skills-ref validate ./skills/my-skill
```

## Citations
```

---

### Example 2 — end of document triggers missing close

**Input (broken):**

```markdown
Keep inline citation format:

```markdown
According to the agentskills.io specification, the `name` field must match
the directory name exactly.
```

**Fixed output:**

```markdown
Keep inline citation format:

```markdown
According to the agentskills.io specification, the `name` field must match
the directory name exactly.
```
```

---

## Edge cases

| Situation | Handling |
|-----------|----------|
| Nested backtick fences (four backticks) | Track fence depth; a four-backtick opener closes with four backticks |
| Inline backticks (single or double) | Ignored — only triple-backtick fences are relevant |
| Indented code blocks (4 spaces) | Not affected by this skill |
| Fence with language hint | Opening fence; closing fence has no hint |
| Multiple consecutive unclosed blocks | Fix each one individually in document order |

---

## Attribution

```
fix-unclosed-fenced-block-en — part of the roebi agent-skills library
Author : roebi (Robert Halter), Switzerland
License: CC BY-NC-SA 4.0  https://creativecommons.org/licenses/by-nc-sa/4.0/
Spec   : https://agentskills.io/specification
Source : https://github.com/roebi/agent-skills
```
