# URL Translation Reference

`create-proxy.py` accepts five GitHub URL forms and translates them all
to a raw content URL for fetching `SKILL.md`.

## Translation rules

### Form 1 — Repo root (no path)
```
Input:  https://github.com/observerw/skill-container
Output: https://raw.githubusercontent.com/observerw/skill-container/main/SKILL.md
Branch: main (assumed)
Path:   SKILL.md (assumed at repo root)
```

### Form 2 — Tree root (branch specified)
```
Input:  https://github.com/observerw/skill-container/tree/main
Output: https://raw.githubusercontent.com/observerw/skill-container/main/SKILL.md
Branch: main (from URL)
Path:   SKILL.md (assumed at repo root)
```

### Form 3 — Tree path (skill in subdirectory)
```
Input:  https://github.com/observerw/skill-container/tree/main/skills/my-skill
Output: https://raw.githubusercontent.com/observerw/skill-container/main/skills/my-skill/SKILL.md
Branch: main (from URL)
Path:   skills/my-skill/SKILL.md (derived — SKILL.md appended to path)
```

### Form 4 — Blob file (direct file link as seen when reading SKILL.md on GitHub)
```
Input:  https://github.com/observerw/skill-container/blob/main/SKILL.md
Output: https://raw.githubusercontent.com/observerw/skill-container/main/SKILL.md
Branch: main (from URL)
Path:   SKILL.md (from URL)
```

### Form 5 — Raw URL (used as-is)
```
Input:  https://raw.githubusercontent.com/observerw/skill-container/main/SKILL.md
Output: https://raw.githubusercontent.com/observerw/skill-container/main/SKILL.md
```

Also normalises `refs/heads/branch` → `branch`:
```
Input:  https://raw.githubusercontent.com/observerw/skill-container/refs/heads/main/SKILL.md
Output: https://raw.githubusercontent.com/observerw/skill-container/main/SKILL.md
```

## Pinned URL (after commit hash is fetched)

The branch-based raw URL is immediately replaced with a commit-pinned URL:
```
https://raw.githubusercontent.com/observerw/skill-container/<commit-sha>/SKILL.md
```

GitHub guarantees content at a commit SHA never changes — even if the
branch is force-pushed or the file is later modified.

This pinned URL is stored in `proxy-raw-url` in the proxy SKILL.md metadata.
The branch name is stored separately in `proxy-branch` for informational
purposes only.
