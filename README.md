# roebi/agent-skills

Agent Skills following the [agentskills.io](https://agentskills.io) open specification.

## Skills

| Skill | Description |
|-------|-------------|
| [`apply-tdd-loop-en`](skills/apply-tdd-loop-en/) | Applies the Test-Driven Development (TDD) cycle as an agentic RED -> GREEN -> REFACTOR loop |
| [`brainstorming-topic-dialog-creative-mentor-en`](skills/brainstorming-topic-dialog-creative-mentor-en/) | Interactive brainstorming mentor dialog that builds an idea-tree and produces a summary |
| [`create-agent-skill-en`](skills/create-agent-skill-en/) | Scaffold a new Agent Skill following the agentskills.io specification |
| [`create-awesome-readme-en`](skills/create-awesome-readme-en/) | Generate a curated awesome-list README from GitHub topic search results |
| [`create-file-tree-for-topic-en`](skills/create-file-tree-for-topic-en/) | Scaffold a topic-specific directory and file tree with README and placeholders |
| [`create-impressum-ch-en`](skills/create-impressum-ch-en/) | Create a Swiss-law-compliant Impressum (legal notice) in German and English |
| [`create-openscad-from-construction-image-en`](skills/create-openscad-from-construction-image-en/) | Convert a construction sketch or photo into a valid OpenSCAD (.scad) file |
| [`create-privacy-policy-ch-en`](skills/create-privacy-policy-ch-en/) | Generate a Swiss-law-compliant privacy policy (Datenschutzerklärung) |
| [`create-python-project-github-en`](skills/create-python-project-github-en/) | Scaffold a modern Python project with packaging, CI, and best practices |
| [`create-questions-and-answers-en`](skills/create-questions-and-answers-en/) | Run a structured Q&A loop and compile questions/answers into a Markdown file |
| [`create-skill-proxy-en`](skills/create-skill-proxy-en/) | Create a local proxy that pins a remote Agent Skill from GitHub to a commit |
| [`fix-unclosed-fenced-block-en`](skills/fix-unclosed-fenced-block-en/) | Detect and fix unclosed fenced code blocks in Markdown |
| [`fortune-cowsay-en`](skills/fortune-cowsay-en/) | Run `fortune` piped through `cowsay` to produce ASCII-art fortunes and save output |
| [`learn-topic-having-teacher-track-learning-progress`](skills/learn-topic-having-teacher-track-learning-progress/) | Teacher-guided 5-level learning plan with a living progress file for a topic |
| [`move-skills-to-new-nameconvention-license-en`](skills/move-skills-to-new-nameconvention-license-en/) | Bulk-rename skills and set SKILL.md `license` fields to CC BY-NC-SA 4.0 |
| [`project-bootstrap-en`](skills/project-bootstrap-en/) | Recommend a local LLM and initial skills for bootstrapping a software project |
| [`quick-documentation-en`](skills/quick-documentation-en/) | Generate concise JSDoc comments or Python docstrings for code blocks |
| [`session-git-lifecycle-en`](skills/session-git-lifecycle-en/) | Git-based session lifecycle: CREATE and RESUME procedures for agent sessions |
| [`skill-container-proxy-en`](skills/skill-container-proxy-en/) | Proxy to package or migrate skills into a container/OCI Skill Container format |
| [`terminal-cli-en`](skills/terminal-cli-en/) | Reference for operating in a Unix/Linux terminal and common CLI workflows |
| [`translate-skill-de`](skills/translate-skill-de/) | Translate an existing Agent Skill into German (UTF-8) |
| [`translate-skill-en`](skills/translate-skill-en/) | Translate an existing Agent Skill into English (UTF-8) |

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
    "https://github.com/roebi/agent-skills/tree/main/skills/apply-tdd-loop-en",
    "https://github.com/roebi/agent-skills/tree/main/skills/brainstorming-topic-dialog-creative-mentor-en",
    "https://github.com/roebi/agent-skills/tree/main/skills/create-agent-skill-en",
    "https://github.com/roebi/agent-skills/tree/main/skills/create-awesome-readme-en",
    "https://github.com/roebi/agent-skills/tree/main/skills/create-file-tree-for-topic-en",
    "https://github.com/roebi/agent-skills/tree/main/skills/create-impressum-ch-en",
    "https://github.com/roebi/agent-skills/tree/main/skills/create-openscad-from-construction-image-en",
    "https://github.com/roebi/agent-skills/tree/main/skills/create-privacy-policy-ch-en",
    "https://github.com/roebi/agent-skills/tree/main/skills/create-python-project-github-en",
    "https://github.com/roebi/agent-skills/tree/main/skills/create-questions-and-answers-en",
    "https://github.com/roebi/agent-skills/tree/main/skills/create-skill-proxy-en",
    "https://github.com/roebi/agent-skills/tree/main/skills/fix-unclosed-fenced-block-en",
    "https://github.com/roebi/agent-skills/tree/main/skills/fortune-cowsay-en",
    "https://github.com/roebi/agent-skills/tree/main/skills/learn-topic-having-teacher-track-learning-progress",
    "https://github.com/roebi/agent-skills/tree/main/skills/move-skills-to-new-nameconvention-license-en",
    "https://github.com/roebi/agent-skills/tree/main/skills/project-bootstrap-en",
    "https://github.com/roebi/agent-skills/tree/main/skills/quick-documentation-en",
    "https://github.com/roebi/agent-skills/tree/main/skills/session-git-lifecycle-en",
    "https://github.com/roebi/agent-skills/tree/main/skills/skill-container-proxy-en",
    "https://github.com/roebi/agent-skills/tree/main/skills/terminal-cli-en",
    "https://github.com/roebi/agent-skills/tree/main/skills/translate-skill-en",
    "https://github.com/roebi/agent-skills/tree/main/skills/translate-skill-de"
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
skills-ref validate ./skills/apply-tdd-loop-en
skills-ref validate ./skills/brainstorming-topic-dialog-creative-mentor-en
skills-ref validate ./skills/create-agent-skill-en
skills-ref validate ./skills/create-awesome-readme-en
skills-ref validate ./skills/create-file-tree-for-topic-en
skills-ref validate ./skills/create-impressum-ch-en
skills-ref validate ./skills/create-openscad-from-construction-image-en
skills-ref validate ./skills/create-privacy-policy-ch-en
skills-ref validate ./skills/create-python-project-github-en
skills-ref validate ./skills/create-questions-and-answers-en
skills-ref validate ./skills/create-skill-proxy-en
skills-ref validate ./skills/fix-unclosed-fenced-block-en
skills-ref validate ./skills/fortune-cowsay-en
skills-ref validate ./skills/learn-topic-having-teacher-track-learning-progress
skills-ref validate ./skills/move-skills-to-new-nameconvention-license-en
skills-ref validate ./skills/project-bootstrap-en
skills-ref validate ./skills/quick-documentation-en
skills-ref validate ./skills/session-git-lifecycle-en
skills-ref validate ./skills/skill-container-proxy-en
skills-ref validate ./skills/terminal-cli-en
skills-ref validate ./skills/translate-skill-en
skills-ref validate ./skills/translate-skill-de
```

## Contributing

Pull requests welcome. Please ensure:

1. Your skill passes `skills-ref validate` before submitting
2. The skill directory name matches the `name` field in `SKILL.md`
3. The skill follows the naming conventions table above

## License

[CC BY-NC-SA 4.0](LICENSE)
