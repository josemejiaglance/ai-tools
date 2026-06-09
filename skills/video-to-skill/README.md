# Video to Skill

An [Agent Skill](https://agentskills.io) that turns video and transcript content into reusable skills — or updates existing ones. Works with Cursor, Codex, Claude Code, and any agent that supports the open standard.

## Install

```bash
# Cursor — project (recommended)
npx skills add josemejiaglance/ai-tools@video-to-skill -a cursor -y

# Cursor — global
npx skills add josemejiaglance/ai-tools@video-to-skill -a cursor -g -y

# Open standard / other agents
npx skills add josemejiaglance/ai-tools@video-to-skill -y
```

**Cursor paths:** `.cursor/skills/video-to-skill/` (project) or `~/.cursor/skills/video-to-skill/` (global `-g`). Bundles `scripts/` and `requirements.txt`.

If `npx skills` places a project copy under `.agents/skills/` instead, symlink it into `.cursor/skills/` so `@video-to-skill` resolves:

```bash
ln -sf ../.agents/skills/video-to-skill .cursor/skills/video-to-skill
```

For open-standard / multi-agent layout, omit `-a cursor` — installs to `.agents/skills/video-to-skill/`.

## What it does

1. Loads transcripts from YouTube, Google Meet, Zoom, Teams, Loom, and other sources
2. Clusters content into a main subject and subcategories
3. Builds a skill with progressive disclosure (`SKILL.md` + `reference.md`)
4. Validates that each section adds delta knowledge beyond what the agent already knows
5. Merges new content into existing skills when you ask to update one

## Python setup

| Install | Path |
|---------|------|
| Cursor, project | `.cursor/skills/video-to-skill/` |
| Cursor, global (`-g`) | `~/.cursor/skills/video-to-skill/` |
| Open standard, project | `.agents/skills/video-to-skill/` |
| Cloned from git | `skills/video-to-skill/` |

```bash
cd .cursor/skills/video-to-skill   # adjust path for your install scope
python3 -m pip install -r requirements.txt
python3 scripts/load_transcript.py "https://youtu.be/VIDEO_ID" -o /tmp/transcript.json
```

## Usage

```
@video-to-skill
```

### Create a skill

> Create a skill from https://www.youtube.com/watch?v=VIDEO_ID — only the Playwright sections

### Update an existing skill

Before creating anything new, the agent searches `~/.cursor/skills/`, `~/.agents/skills/`, and other standard paths (via Glob/Read) for a match — then offers to **update in place** instead of asking where to save.

> Update `@playwright` from this YouTube link — flakiness section only

### Multi-source

> Create a Playwright skill from this YouTube link AND our Meet recording (`sprint.vtt`)

## Supported sources

| Provider | Auto-fetch | Input |
|----------|------------|-------|
| YouTube | Yes | URL or video ID |
| Google Meet | No | `.sbv` file, pasted notes |
| Zoom | No | `.vtt` from cloud recording |
| Microsoft Teams | No | `.vtt` from meeting recap |
| Loom | No | `.txt` export or paste |
| Vimeo | No | `.vtt` captions |
| Pasted text | N/A | Inline in chat or via CLI |

Export guides: [providers.md](providers.md)

## Project layout

```
skills/video-to-skill/
├── SKILL.md              # Agent workflow
├── scripts/              # Transcript loaders
├── requirements.txt
├── providers.md
└── *-template.md         # Output templates
```
