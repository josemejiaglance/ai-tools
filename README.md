# ai-tools

Tools and [Agent Skills](https://agentskills.io) for turning videos and transcripts into reusable skills. Works with Cursor, Codex, Claude Code, and any agent that supports the open standard.

## Install

Use the [skills CLI](https://github.com/vercel-labs/skills) — no clone required:

```bash
# Cursor (recommended) — project install
npx skills add josemejiaglance/ai-tools@video-to-skill -a cursor -y

# Cursor — global install (all projects)
npx skills add josemejiaglance/ai-tools@video-to-skill -a cursor -g -y

# Other agents (open-standard layout)
npx skills add josemejiaglance/ai-tools@video-to-skill -y
```

Then invoke `@video-to-skill` in your agent and provide a YouTube URL, meeting caption file, or pasted transcript. Generated skills are written to a project directory you choose (`.cursor/skills/`, `.agents/skills/`, etc.) — never to global paths.

Browse more skills at [skills.sh](https://skills.sh/).

## What it does

The **video-to-skill** skill:

1. Loads transcripts from YouTube, Google Meet, Zoom, Teams, Loom, and other sources
2. Clusters content into a main subject and subcategories
3. Generates `SKILL.md` + `reference.md` following the Agent Skills standard
4. Creates or updates skills **in the current project only** (replace, modify, or add)

## Python setup

After installing, set up transcript tooling from the skill directory:

| Install | Path |
|---------|------|
| Cursor, project | `.cursor/skills/video-to-skill/` |
| Cursor, global (`-g`) | `~/.cursor/skills/video-to-skill/` |
| Open standard, project | `.agents/skills/video-to-skill/` |
| Open standard, global | `~/.agents/skills/video-to-skill/` |

> **Note:** `npx skills` may place a *project* copy under `.agents/skills/` even with `-a cursor`. Cursor loads `@video-to-skill` from `.cursor/skills/` — use `-g` for a global install, or symlink: `ln -sf ../.agents/skills/video-to-skill .cursor/skills/video-to-skill`

```bash
cd .cursor/skills/video-to-skill   # adjust path for your install scope
python3 -m pip install -r requirements.txt
```

## Clone for development

```bash
git clone git@github.com:josemejiaglance/ai-tools.git
cd ai-tools
```

See [skills/video-to-skill/README.md](skills/video-to-skill/README.md) for full workflow details.

## Project structure

```
ai-tools/
├── skills/
│   └── video-to-skill/     # Skill + scripts + documentation
└── skills.sh.json
```

## Requirements

- `npx skills` for one-command install
- Python 3.10+ for transcript tooling
- An AI coding agent with Agent Skills support

## License

Use and adapt freely.
