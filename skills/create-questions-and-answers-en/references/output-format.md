# Output Format Reference

Extended formatting guide for the compiled Q&A Markdown file.

## Session header

```markdown
# Q&A Session: <Topic Title>

> <One sentence describing the session context, e.g. "Testing the systemprompt
> configuration for roebi's agent-skills setup.">
> Date: YYYY-MM-DD

---
```

## Per-question block

```markdown
## Q<N>: <Short descriptive title>

**Question:**
<Exact question as the user wrote it>

**Answer:**
<Full answer. May include:>
- Bullet lists
- Tables
- Code blocks
- Citations / links
- Sub-headings if the answer is long

---
```

## Tables in answers

Preserve all Markdown tables verbatim:

```markdown
| Column A | Column B |
|---|---|
| value    | value    |
```

## Code blocks in answers

Preserve language hints:

```markdown
```bash
skills-ref validate ./skills/my-skill
```
```

## Citations

Keep inline citation format if used during the session:

```markdown
According to the agentskills.io specification, the `name` field must match
the directory name exactly.
```

## File naming

| Session topic | File name |
|---|---|
| System prompt testing | `systemprompt-qa-session.md` |
| Agent skills overview | `agent-skills-qa-session.md` |
| Project review | `project-review-qa-session.md` |
| General / untitled | `qa-session-YYYY-MM-DD.md` |
