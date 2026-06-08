# Skills Generator

Turn videos, meeting recordings, and transcripts into [Agent Skills](https://agentskills.io) for any AI coding agent.

## Install

```bash
npx skills add josemejiaglance/ai-tools@video-to-skill -y
```

Then invoke `@video-to-skill` in your agent and provide a source.

## What it does

1. Loads transcripts from YouTube, Google Meet, Zoom, Teams, Loom, and other sources
2. Clusters content into a main subject and subcategories
3. Builds a skill with progressive disclosure (`SKILL.md` + `reference.md`)
4. Validates that each section adds delta knowledge beyond what the agent already knows
5. Merges new content into existing skills when you ask to update one

## Python setup

```bash
cd .agents/skills/video-to-skill   # or skills/video-to-skill when cloned
python3 -m pip install -r requirements.txt
python3 scripts/load_transcript.py "https://youtu.be/VIDEO_ID" -o /tmp/transcript.json
```

## Usage

```
@video-to-skill
```

Examples:

> Create a skill from https://www.youtube.com/watch?v=EXAMPLE — Playwright topics only

> Update `@playwright` from this YouTube link — flakiness section only

> Create a skill from this YouTube link AND our Meet recording (`sprint.vtt`)

## Project layout

```
ai-tools/
├── skills/
│   └── video-to-skill/
│       ├── scripts/            # Transcript loaders
│       └── requirements.txt
└── skills-generator/           # This documentation
```

## Supported transcript sources

| Provider | Auto-fetch | Input |
|----------|------------|-------|
| YouTube | Yes | URL or video ID |
| Google Meet | No | `.sbv` file, pasted notes |
| Zoom | No | `.vtt` from cloud recording |
| Microsoft Teams | No | `.vtt` from meeting recap |
| Loom | No | `.txt` export or paste |
| Pasted text | N/A | Inline in chat or via CLI |

Export guides: [skills/video-to-skill/providers.md](../skills/video-to-skill/providers.md)
