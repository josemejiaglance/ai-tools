# ai-tools

Tools and [Agent Skills](https://agentskills.io) for turning videos and transcripts into reusable skills. Works with Cursor, Codex, Claude Code, and any agent that supports the open standard.

## Install

Use the [skills CLI](https://github.com/vercel-labs/skills) — no clone required:

```bash
# Install the skill generator
npx skills add josemejiaglance/ai-tools@video-to-skill

# Install for a specific agent, skip prompts
npx skills add josemejiaglance/ai-tools@video-to-skill -a cursor -y

# Install globally (all projects)
npx skills add josemejiaglance/ai-tools@video-to-skill -g -y
```

Then invoke `@video-to-skill` in your agent and provide a YouTube URL, meeting caption file, or pasted transcript.

Browse more skills at [skills.sh](https://skills.sh/).

## What it does

The **video-to-skill** skill:

1. Loads transcripts from YouTube, Google Meet, Zoom, Teams, Loom, and other sources
2. Clusters content into a main subject and subcategories
3. Generates `SKILL.md` + `reference.md` following the Agent Skills standard
4. Updates existing skills with new knowledge when you ask

## Python setup

After installing, set up transcript tooling:

```bash
cd .agents/skills/video-to-skill   # or ~/.agents/skills/video-to-skill with -g
python3 -m pip install -r requirements.txt
```

## Clone for development

```bash
git clone git@github.com:josemejiaglance/ai-tools.git
cd ai-tools
```

See [skills-generator/README.md](skills-generator/README.md) for full workflow details.

## Project structure

```
ai-tools/
├── skills/
│   └── video-to-skill/     # Skill generator + bundled transcript scripts
├── skills-generator/       # Documentation
└── skills.sh.json
```

## Requirements

- `npx skills` for one-command install
- Python 3.10+ for transcript tooling
- An AI coding agent with Agent Skills support

## License

Use and adapt freely.
