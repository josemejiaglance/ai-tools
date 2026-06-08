# Skills Generator

Turn videos, meeting recordings, and transcripts into [Agent Skills](https://agentskills.io) — portable skill packages for any AI coding agent.

## Quick install

No need to clone this repo. Install skills with one command:

```bash
# List skills
npx skills add josemejiaglance/ai-tools --list

# Install the meta-skill (creates skills from videos)
npx skills add josemejiaglance/ai-tools@video-to-skill -y

# Install the example Checkly skill
npx skills add josemejiaglance/ai-tools@checkly -y
```

Then invoke `@video-to-skill` in your agent and provide a YouTube URL or transcript.

## What it does

The **video-to-skill** workflow:

1. Loads transcripts from YouTube, Google Meet, Zoom, Teams, Loom, and other sources
2. Clusters content into a main subject and subcategories
3. Builds a skill with progressive disclosure (`SKILL.md` + `reference.md`)
4. Validates that each section adds delta knowledge beyond what the agent already knows

## Python setup (for video-to-skill)

After installing via `npx skills add`, set up transcript tooling from the installed skill directory:

```bash
# Find your install path (usually .agents/skills/video-to-skill)
cd .agents/skills/video-to-skill   # or ~/.agents/skills/video-to-skill with -g

python3 -m pip install -r requirements.txt
python3 scripts/load_transcript.py "https://youtu.be/VIDEO_ID" -o /tmp/transcript.json
```

When developing from a clone, use `skills/video-to-skill/` instead.

## Usage with your agent

```
@video-to-skill
```

Example:

> Create a skill from https://www.youtube.com/watch?v=EXAMPLE — Playwright topics only

## Project layout

```
ai-tools/
├── skills/                     # Canonical skill packages (install via npx)
│   ├── video-to-skill/
│   │   ├── scripts/            # Transcript loaders
│   │   └── requirements.txt
│   └── checkly/                # Example generated skill
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

## Example output

[checkly](../skills/checkly/) was generated from a YouTube webinar. See its [README](../skills/checkly/README.md).
