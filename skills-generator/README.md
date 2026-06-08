# Skills Generator

Turn videos, meeting recordings, and transcripts into [Cursor Agent Skills](https://cursor.com/docs/context/skills) — or update existing skills with new knowledge.

## What it does

The **video-to-skill** workflow:

1. Loads transcripts from YouTube, Google Meet, Zoom, Teams, Loom, and other sources
2. Clusters content into a main subject and subcategories
3. Builds a skill with progressive disclosure (`SKILL.md` + `reference.md`)
4. Validates that each section adds delta knowledge beyond what the agent already knows

## Setup

Install Python dependencies once per machine:

```bash
cd skills-generator
python3 -m pip install -r requirements.txt
```

## Usage

### In Cursor

Open this repository (or copy `.cursor/skills/` into your project) and invoke the meta-skill:

```
@video-to-skill
```

Then provide a source:

- YouTube URL — auto-fetched
- Meeting caption file (`.vtt`, `.sbv`, `.srt`)
- Pasted transcript text

Example:

> Create a skill from https://www.youtube.com/watch?v=EXAMPLE — Playwright topics only

The agent walks through topic confirmation, scope filtering, and skill file generation.

### CLI — load transcripts manually

From the `skills-generator/` directory:

```bash
# YouTube
python3 scripts/load_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID" -o /tmp/transcript.json

# Meeting caption file
python3 scripts/load_transcript.py meeting.vtt --source google-meet -o /tmp/transcript.json

# Multiple sources
python3 scripts/load_transcript.py "https://youtu.be/VIDEO_ID" meeting.vtt --merge -o /tmp/transcript.json

# Filter by time range (seconds)
python3 scripts/load_transcript.py "https://youtu.be/VIDEO_ID" --start 300 --end 720 -o /tmp/filtered.json
```

See [scripts/README.md](scripts/README.md) for full CLI reference.

## Project structure

```
skills-generator/
├── .cursor/skills/
│   ├── video-to-skill/     # Meta-skill — create/update skills from video
│   └── checkly/            # Example output — Checkly network monitoring
├── scripts/
│   ├── load_transcript.py  # Unified transcript loader (preferred)
│   ├── fetch_transcript.py # YouTube-only fetcher (legacy)
│   └── transcript_formats.py
├── requirements.txt
└── README.md
```

## Supported sources

| Provider | Auto-fetch | Input |
|----------|------------|-------|
| YouTube | Yes | URL or video ID |
| Google Meet | No | `.sbv` file, pasted notes |
| Zoom | No | `.vtt` from cloud recording |
| Microsoft Teams | No | `.vtt` from meeting recap |
| Loom | No | `.txt` export or paste |
| Vimeo | No | `.vtt` captions |
| Otter / Fireflies / Grain | No | `.txt` / `.srt` export |
| Pasted text | N/A | Inline in chat or via CLI |

Export guides for each platform: [.cursor/skills/video-to-skill/providers.md](.cursor/skills/video-to-skill/providers.md)

## Skill output format

Generated skills follow Cursor best practices:

```
skill-name/
├── SKILL.md        # Routing layer — quick reference, agent instructions
├── reference.md    # Depth layer — full guidance per subcategory
└── examples.md     # Optional — only when 4+ copy-paste examples
```

Install generated skills in:

- `.cursor/skills/<name>/` — project-scoped (team sharing)
- `~/.cursor/skills/<name>/` — personal (all workspaces)

## Example skill

[checkly/](.cursor/skills/checkly/) was generated from a YouTube webinar and demonstrates the expected output structure. See its [README](.cursor/skills/checkly/README.md) for install and usage.

## Requirements

- Python 3.10+
- `youtube-transcript-api` (see `requirements.txt`)
- [Cursor](https://cursor.com) with Agent Skills enabled
