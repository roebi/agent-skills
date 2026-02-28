# roebi/agent-skills

Agent Skills following the [agentskills.io](https://agentskills.io) open specification.

## Skills

| Skill | Description |
|-------|-------------|
| [`create-agent-skill`](skills/create-agent-skill/) | Scaffold a new Agent Skill following the agentskills.io spec |
| [`create-awesome-readme`](skills/create-awesome-readme/) | Generate a curated awesome-list README from a GitHub topic tag |
| [`terminal-cli`](skills/terminal-cli/) | Reference for operating in a Linux terminal |

## Install

### With skillport (recommended)

```bash
skillport install github:roebi/agent-skills
```

### Manual (Claude Code)

Add to your `.claude/settings.json`:

```json
{
  "skills": [
    "https://github.com/roebi/agent-skills/tree/main/skills/create-agent-skill",
    "https://github.com/roebi/agent-skills/tree/main/skills/create-awesome-readme",
    "https://github.com/roebi/agent-skills/tree/main/skills/terminal-cli"
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
skills-ref validate ./skills/create-agent-skill
skills-ref validate ./skills/create-awesome-readme
skills-ref validate ./skills/terminal-cli
```

## Contributing

Pull requests welcome. Please ensure your skill passes `skills-ref validate`
before submitting.

## License

[Apache-2.0](LICENSE)
