---
name: move-skills-to-new-nameconvention-license-en
description: Renames all agent skills in a GitHub repository by appending a postfix to each skill's folder name and SKILL.md name field, and sets the license field in each SKILL.md frontmatter to CC BY-NC-SA 4.0. Reentrant and idempotent — safe to run multiple times with the same or a different postfix. Use this skill when a user wants to bulk-rename skills with a new naming convention, update the license field in skill frontmatter, or both — triggered by phrases like "rename my skills", "add postfix to skills", "update license field", "apply new naming convention to agent skills", or "prepare skills for new license".
license: CC BY-NC-SA 4.0
---

# move-skills-to-new-nameconvention-license-en

Renames all agent skills in a repository and sets `license: CC BY-NC-SA 4.0` in every `SKILL.md` frontmatter (Attribution-NonCommercial-ShareAlike 4.0 International — https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode.en).

**Prerequisites — done manually by you before running this skill:**
- Feature branch already created and checked out
- New LICENSE file already added to the repo root

**This skill only does:**
- Rename each skill folder with the postfix
- Update `name:` in each `SKILL.md`
- Upsert `license: CC BY-NC-SA 4.0` in each `SKILL.md` frontmatter
- Commit the result

**Reentrant:** Excludes itself from renaming. Skips folders already ending with `$POSTFIX`. Safe to run multiple times.

---

## Inputs

| Parameter | Description | Example |
|---|---|---|
| `REPO_PATH` | Local path to the cloned git repository | `/home/user/agent-skills` |
| `POSTFIX` | Suffix to append to every skill name | `-en` |

The license value written into every `SKILL.md` is fixed:
```
license: CC BY-NC-SA 4.0
```

---

## Steps

### 1. Validate inputs

```bash
cd "$REPO_PATH"
git status || { echo "ERROR: Not a git repository: $REPO_PATH"; exit 1; }
[ -n "$POSTFIX" ] || { echo "ERROR: POSTFIX must not be empty"; exit 1; }
[ -d "$REPO_PATH/skills" ] || { echo "ERROR: No skills/ directory found in repo"; exit 1; }

echo "Current branch: $(git branch --show-current)"
echo "Working on: $REPO_PATH"
```

---

### 2. Define the license upsert helper

Define this before the main loop:

```bash
LICENSE_VALUE="CC BY-NC-SA 4.0"

_upsert_license() {
  local FILE="$1"

  if grep -q "^license:" "$FILE"; then
    # Replace existing license line — no-op if already correct
    sed -i.bak "s|^license:.*|license: ${LICENSE_VALUE}|" "$FILE"
  else
    # Insert license: after the description: line
    sed -i.bak "/^description:/a\\
license: ${LICENSE_VALUE}" "$FILE"
  fi
  rm -f "${FILE}.bak"
  echo "  license: → ${LICENSE_VALUE}"
}
```

> **macOS note:** BSD `sed -i` requires the `.bak` suffix — it is removed immediately.

---

### 3. Process each skill folder

```bash
SELF="move-skills-to-new-nameconvention-license-en"

cd "$REPO_PATH/skills"

for SKILL_DIR in */; do
  SKILL_DIR="${SKILL_DIR%/}"

  [ -d "$SKILL_DIR" ] || continue

  # Guard 1: self — skip rename, still update license
  if [ "$SKILL_DIR" = "$SELF" ]; then
    echo "SKIP rename (self): $SKILL_DIR"
    [ -f "$SKILL_DIR/SKILL.md" ] && _upsert_license "$SKILL_DIR/SKILL.md"
    continue
  fi

  # Guard 2: already has postfix — skip rename, still update license
  if [[ "$SKILL_DIR" == *"$POSTFIX" ]]; then
    echo "SKIP rename (already has postfix): $SKILL_DIR"
    [ -f "$SKILL_DIR/SKILL.md" ] && _upsert_license "$SKILL_DIR/SKILL.md"
    continue
  fi

  NEW_NAME="${SKILL_DIR}${POSTFIX}"

  # Rename folder
  git mv "$SKILL_DIR" "$NEW_NAME"
  echo "Renamed: $SKILL_DIR → $NEW_NAME"

  SKILL_MD="$NEW_NAME/SKILL.md"
  if [ -f "$SKILL_MD" ]; then
    # Update name: field (no-op if already updated)
    sed -i.bak "s/^name: ${SKILL_DIR}$/name: ${NEW_NAME}/" "$SKILL_MD"
    rm -f "${SKILL_MD}.bak"
    echo "  name: ${SKILL_DIR} → ${NEW_NAME}"
    _upsert_license "$SKILL_MD"
  else
    echo "  WARNING: No SKILL.md found in $NEW_NAME"
  fi
done
```

---

### 4. Commit

```bash
cd "$REPO_PATH"
git add skills/

if ! git diff --cached --quiet; then
  git commit -m "chore: rename skills with postfix '${POSTFIX}', set license CC BY-NC-SA 4.0

- Appended '${POSTFIX}' to all skill folder names and name fields
- Set license: CC BY-NC-SA 4.0 in all SKILL.md frontmatters
- Excluded self: ${SELF} (license field still updated)
- Reentrant: already-renamed skills were skipped"
else
  echo "Nothing to commit — already up to date."
fi
```

---

### 5. Verify

```bash
echo ""
echo "=== Summary ==="
echo "Branch : $(git branch --show-current)"
echo ""
echo "Skills:"
ls "$REPO_PATH/skills/"
echo ""
echo "Sample frontmatter (first skill):"
head -6 "$REPO_PATH/skills/$(ls "$REPO_PATH/skills/" | head -1)/SKILL.md"
echo ""
git log -1 --stat
```

---

## Reentrant behaviour

| Situation | Behaviour |
|---|---|
| Same `POSTFIX` run again | Rename skipped; `license:` upsert is a no-op if already correct |
| Different `POSTFIX` after a first run | Old-postfix folders don't match → renamed again, license updated |
| Self folder | Rename always skipped; license field still updated |
| `license:` already correct | `sed` replaces with same value — no effective change |
| `license:` absent | Inserted after `description:` line |
| Nothing changed | Commit step prints "Nothing to commit" |

---

## Example run (first time, POSTFIX=`-en`)

```
Current branch: feature/rename-skills-en-cc-by-nc-sa
SKIP rename (self): move-skills-to-new-nameconvention-license-en
  license: → CC BY-NC-SA 4.0
Renamed: create-skill-proxy → create-skill-proxy-en
  name: create-skill-proxy → create-skill-proxy-en
  license: → CC BY-NC-SA 4.0
Renamed: another-skill → another-skill-en
  name: another-skill → another-skill-en
  license: → CC BY-NC-SA 4.0

[feature/rename-skills-en-cc-by-nc-sa abc1234] chore: rename skills ...
```

## Example run (second time — reentrant)

```
Current branch: feature/rename-skills-en-cc-by-nc-sa
SKIP rename (self): move-skills-to-new-nameconvention-license-en
  license: → CC BY-NC-SA 4.0
SKIP rename (already has postfix): create-skill-proxy-en
  license: → CC BY-NC-SA 4.0
SKIP rename (already has postfix): another-skill-en
  license: → CC BY-NC-SA 4.0

Nothing to commit — already up to date.
```
