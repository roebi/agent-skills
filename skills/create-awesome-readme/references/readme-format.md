# Awesome README Format Reference

The generated `README.md` follows the
[sindresorhus/awesome](https://github.com/sindresorhus/awesome) conventions
with additions for Agent Skills labeling.

## Structure

```
# Awesome Agent Skills · `<tag>`

> Description + spec link

[![Awesome badge]](https://awesome.re)

*Auto-generated · N repos analyzed · Last updated: YYYY-MM-DD*

## Summary
Table: category → count (including misleading / security signal counts)

## Label Legend
Table: label → meaning + icon

## 📦 Skill Collections
*Repositories containing multiple Agent Skills.*

- **[owner/repo](url)** — description ⭐ N `language` `spec-compliant` ✅

## 🎯 Individual Skills
...

## 🛠️ Skill Managers & Registries
...

## 🔌 Integrations & Tooling
...

## 📋 Other Awesome Lists
...

## 🏗️ Frameworks & SDKs
...

## 💡 Examples & Demos
...

## 🔍 Other
(off-topic, misleading, or unclassified)

---

## Contributing
## License
```

## Entry line format

```
- **[owner/name](https://github.com/owner/name)** — description ⭐ STARS `LANG` SIGNALS
```

Example entries:

```markdown
- **[anthropics/skills](https://github.com/anthropics/skills)** — Official Anthropic example skills ⭐ 234 `Python` `spec-compliant` ✅ `multi-agent` 🌐 `has-references` 📚

- **[badactor/sketch](https://github.com/badactor/sketch)** — Sketching tool ⭐ 2 `Python` `misleading` ⚠️ `no-license` 🔓

- **[dangerous/cleaner](https://github.com/dangerous/cleaner)** — Clean your workspace ⭐ 1 `Shell` `rm-rf` 💥
```

## Section ordering rationale

Categories are ordered by specificity and usefulness to the reader:
1. Skill collections — most directly useful to agents
2. Individual skills — directly useful
3. Managers — tooling to work with skills
4. Integrations — agents/products that consume skills
5. Awesome lists — meta
6. Frameworks — infrastructure
7. Examples — learning resources
8. Other — catch-all, includes misleading repos (for transparency)

Misleading and off-topic repos are **not hidden** — they are listed in the
"Other" section with the `misleading` label so the list is honest about
what it found.
