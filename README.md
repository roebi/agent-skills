# roebi/agent-skills

Agent Skills following the [agentskills.io](https://agentskills.io) open specification.

## Skills

| Skill | Description |
|-------|-------------|
| [`create-agent-skill-en`](skills/create-agent-skill-en/) | Scaffold a new Agent Skill following the agentskills.io spec |
| [`create-awesome-readme-en`](skills/create-awesome-readme-en/) | Generate a curated awesome-list README from a GitHub topic tag |
| [`create-skill-proxy-en`](skills/create-skill-proxy-en/) | Create a local proxy skill that wraps and pins a remote Agent Skill from GitHub |
| [`skill-container-proxy-en`](skills/skill-container-proxy-en/) | Proxy for skill-container by observerw. Creates new Agent Skills or migrates existing ones into the Skill Container format |
| [`terminal-cli-en`](skills/terminal-cli-en/) | Reference for operating in a Linux terminal |

## Naming conventions

The agentskills.io specification requires that a skill's `name` field in
`SKILL.md` must exactly match its parent directory name. Grouping via
subdirectories is therefore not spec-compliant. All skills live as direct
subdirectories of `skills/` and are distinguished by naming convention only.

| Pattern | Example(s) | Meaning |
|---------|-----------|---------|
| `create-agent-skill` | `create-agent-skill-en` | The meta skill — teaches agents how to author a new spec-compliant skill |
| `create-skill-<type>` | `create-skill-proxy-en`, `create-skill-container` | Skills that scaffold other skills, by output type |
| `create-<artifact>` | `create-awesome-readme-en` | Skills that produce a specific artifact or document |
| `<tool-name>` | `terminal-cli-en` | Plain reference or workflow skill, named after its subject |
| `<n>-proxy` | `skill-container-proxy-en`, `caddy-proxy` | Generated proxy skills wrapping a remote skill — created by `create-skill-proxy` |

Additionally, all skills in this repository append a language code (e.g., `-en` for English, `-de` for German) to indicate the language in which the skill is specified.

**Rule:** all skill directory names (and therefore `name` fields) must be
lowercase, hyphens only, no consecutive hyphens, no leading or trailing hyphens.
Run `skills-ref validate ./skills/<skill-name>` to confirm before pushing.

## Install

### With skillport (recommended)

```bash
skillport install github:roebi/agent-skills
```

### With aider-skills

```bash
pip install aider-skills
# inside an aider session:
/run aider-skills to-prompt ./skills

# or at startup:
aider --read $(aider-skills tmpfile ./skills)
```

See [roebi/aider-skills](https://github.com/roebi/aider-skills) for full usage.

### Manual (Claude Code)

Add to your `.claude/settings.json`:

```json
{
  "skills": [
    "https://github.com/roebi/agent-skills/tree/main/skills/create-agent-skill-en",
    "https://github.com/roebi/agent-skills/tree/main/skills/create-awesome-readme-en",
    "https://github.com/roebi/agent-skills/tree/main/skills/create-skill-proxy-en",
    "https://github.com/roebi/agent-skills/tree/main/skills/fortune-cowsay-en",
    "https://github.com/roebi/agent-skills/tree/main/skills/skill-container-proxy-en",
    "https://github.com/roebi/agent-skills/tree/main/skills/terminal-cli-en"
  ]
}
```

Or clone and reference locally:

```bash
git clone https://github.com/roebi/agent-skills
# then point your agent at ./agent-skills/skills/
```

## Validate

```bash
pip install skills-ref
skills-ref validate ./skills/create-agent-skill-en
skills-ref validate ./skills/create-awesome-readme-en
skills-ref validate ./skills/create-skill-proxy-en
skills-ref validate ./skills/fortune-cowsay-en
skills-ref validate ./skills/skill-container-proxy-en
skills-ref validate ./skills/terminal-cli-en
```

## Contributing

Pull requests welcome. Please ensure:

1. Your skill passes `skills-ref validate` before submitting
2. The skill directory name matches the `name` field in `SKILL.md`
3. The skill follows the naming conventions table above

## License

[CC BY-NC-SA 4.0](LICENSE)
