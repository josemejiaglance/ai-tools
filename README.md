# ai-tools

A collection of [Agent Skills](https://agentskills.io) and tooling for building AI-assisted workflows. Skills work with Cursor, Codex, Claude Code, and any agent that supports the open standard.

## Install skills

Use the [skills CLI](https://github.com/vercel-labs/skills) — no clone required:

```bash
# List available skills
npx skills add josemejiaglance/ai-tools --list

# Install a specific skill
npx skills add josemejiaglance/ai-tools@checkly

# Install video-to-skill (includes Python transcript scripts)
npx skills add josemejiaglance/ai-tools@video-to-skill

# Install to a specific agent
npx skills add josemejiaglance/ai-tools@checkly -a cursor -y

# Install globally (all projects)
npx skills add josemejiaglance/ai-tools@checkly -g -y

# Install all skills
npx skills add josemejiaglance/ai-tools --all -y
```

Browse more skills at [skills.sh](https://skills.sh/).

## Included skills

| Skill | Install | Description |
|-------|---------|-------------|
| **checkly** | `npx skills add josemejiaglance/ai-tools@checkly` | Checkly network monitoring as code — DNS, TCP, ICMP |
| **video-to-skill** | `npx skills add josemejiaglance/ai-tools@video-to-skill` | Turn videos and transcripts into new agent skills |

After installing, invoke in your agent chat — e.g. `@checkly` in Cursor or `/checkly` where slash commands are supported.

## Clone for development

```bash
git clone git@github.com:josemejiaglance/ai-tools.git
cd ai-tools
```

See [skills-generator/README.md](skills-generator/README.md) for the full video-to-skill workflow and Python setup.

## Project structure

```
ai-tools/
├── skills/                 # Installable skills (npx skills add)
│   ├── checkly/
│   └── video-to-skill/     # Includes scripts/ and requirements.txt
├── skills-generator/       # Generator docs and dev notes
└── skills.sh.json          # skills.sh registry metadata
```

## Agent compatibility

Skills follow the [Agent Skills open standard](https://agentskills.io/specification). The skills CLI installs to the right directory for your agent:

| Scope | Paths |
|-------|-------|
| Project | `.agents/skills/`, `.cursor/skills/`, `.claude/skills/`, `.codex/skills/` |
| Personal | `~/.agents/skills/`, `~/.cursor/skills/`, etc. |

## Requirements

- `npx skills` for one-command install (Node.js required for npx only)
- Python 3.10+ for video-to-skill transcript tooling
- An AI coding agent with Agent Skills support

## License

Use and adapt freely. Third-party trademarks belong to their respective owners.
