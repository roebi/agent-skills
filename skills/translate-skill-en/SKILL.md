---
name: translate-skill-en
description: >
  Translates an existing Agent Skill (SKILL.md and all bundled files) from one
  natural language to another. The translated skill is written in English and
  saved as UTF-8. Use this skill whenever a user wants to translate a skill,
  port a skill to another language, make a skill accessible to speakers of a
  different language, or create a language variant of an existing skill.
  Activate for phrases like: "translate this skill", "translate skill from X to
  Y", "make a German version of this skill", "port skill to French",
  "create a language variant", or "translate SKILL.md".
compatibility: >
  Requires read access to the source skill directory or a raw URL.
  Output is UTF-8 encoded. No additional binaries required.
metadata:
  author: roebi-inspired
  spec: https://agentskills.io/specification
  instruction-language: en
  encoding: utf-8
---

# Translate Skill — Instructions in English, UTF-8 Output

Translates an existing Agent Skill from **language A** to **language B**.
All instructions in this skill are written in English. Output files are UTF-8.

---

## When to use this skill

- User provides a SKILL.md (as file, URL, or pasted text) and a target language
- User wants a language variant of an existing skill
- User wants non-English speakers to benefit from an existing skill
- User wants to create `translate-skill-<lang>-utf8` variants of this very skill

---

## What gets translated

| Item | Action |
|------|--------|
| `SKILL.md` frontmatter `description` | Translate to target language |
| `SKILL.md` body (all prose, headings, notes) | Translate to target language |
| `references/*.md` files | Translate each file |
| `scripts/` comments and `--help` text | Translate inline comments and help strings |
| `assets/` text files | Translate if plain text |
| Frontmatter `name` field | **Do NOT translate** — keep original slug |
| Code logic / variable names | **Do NOT translate** — translate comments only |

---

## Step-by-Step Workflow

### Step 1 — Identify source

- Accept: a file path, a raw GitHub URL, or pasted SKILL.md content
- If a URL is given, fetch it with `web_fetch`
- Read all bundled files in `references/`, `scripts/`, `assets/` if present

### Step 2 — Confirm parameters

Ask (or infer from context):
1. **Source language** — what language is the skill currently written in?
2. **Target language** — what language should the output be in?
3. **Output skill name** — default: append `-<lang-code>-utf8` to original name
   - Example: `translate-skill-en` → `translate-skill-de`
4. **Output location** — where to write the translated skill directory?

### Step 3 — Translate SKILL.md

Rules:
- Preserve all YAML frontmatter keys exactly
- Translate `description` value fully into target language
- Add or update `metadata.instruction-language` to reflect target language code
- Keep `metadata.encoding: utf-8`
- Translate all prose in the body
- Keep all code blocks, file paths, URLs, and command examples **untouched**
- Keep the `name` field **untouched**

### Step 4 — Translate bundled files

For each file in `references/`, `scripts/`, `assets/`:
- Translate prose, comments, help text
- Leave code logic, variable names, command syntax untouched
- Save with identical filename in the translated skill directory

### Step 5 — Write output

Create the translated skill directory:
```
<translated-skill-name>/
├── SKILL.md              # translated
├── references/           # translated (if present)
├── scripts/              # translated comments (if present)
└── assets/               # translated text assets (if present)
```

All files saved as **UTF-8**.

### Step 6 — Validate

Check:
- [ ] `name` field unchanged
- [ ] No untranslated prose remaining in SKILL.md body
- [ ] Code blocks intact
- [ ] UTF-8 encoding confirmed (especially for non-Latin scripts)
- [ ] `metadata.instruction-language` updated

### Step 7 — Present

Output the translated skill directory for download.
Briefly summarize: source language → target language, files translated, any
ambiguous terms that were left in source language with a note.

---

## Translation Quality Notes

- **Prefer natural phrasing** over literal word-for-word translation
- **Technical terms** (e.g. "skill", "agent", "SKILL.md", "frontmatter") may be
  kept in English if no natural equivalent exists — add a short note in parentheses
- **Trigger phrases** in the `description` should feel natural to a native speaker
  of the target language — rephrase idiomatically
- **UTF-8 note**: All target languages, including those with non-Latin scripts
  (Japanese, Arabic, Chinese, etc.), are supported via UTF-8 encoding

---

## Example invocations

```
"Translate this skill to German"
→ source: en, target: de, output name: <original>-de-utf8

"Create a French version of translate-skill-en"
→ source: en, target: fr, output name: translate-skill-fr-utf8

"Port this SKILL.md to Japanese"
→ source: en, target: ja, output name: <original>-ja-utf8
```

---

## Self-application: creating language variants of this skill

This skill can translate itself. To create `translate-skill-de`:
1. Use `translate-skill-en` as source
2. Set target language: German (`de`)
3. Output name: `translate-skill-de`
4. The resulting skill is identical in function, but all instructions are in German

---

*This skill follows the [agentskills.io open specification](https://agentskills.io/specification).*
