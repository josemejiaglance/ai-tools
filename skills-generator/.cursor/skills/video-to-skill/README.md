# Video to Skill

A [Cursor Agent Skill](https://cursor.com/docs/context/skills) that turns video and transcript content into reusable skills — or updates existing skills with new knowledge.

## What it does

- Accepts YouTube URLs, meeting caption files, and pasted transcripts
- Supports multiple sources in a single session (e.g. YouTube tutorial + Google Meet recording)
- Clusters content into a main subject and subcategories
- Generates `SKILL.md` + `reference.md` with progressive disclosure
- Detects existing skills and merges new content instead of overwriting

## Requirements

- [Cursor](https://cursor.com) with Agent Skills enabled
- Python 3.10+ with dependencies from [requirements.txt](../../../requirements.txt)

```bash
cd skills-generator
python3 -m pip install -r requirements.txt
```

## Install

### Use from this repository

Open the `ai-tools` repository in Cursor. The skill is available at `.cursor/skills/video-to-skill/`.

### Copy to another project

```bash
cp -r skills-generator/.cursor/skills/video-to-skill /path/to/your-project/.cursor/skills/
```

### Personal install

```bash
mkdir -p ~/.cursor/skills
cp -r skills-generator/.cursor/skills/video-to-skill ~/.cursor/skills/video-to-skill
```

## Usage

In Cursor Agent chat:

```
@video-to-skill
```

### Create a new skill

> Create a skill from https://www.youtube.com/watch?v=VIDEO_ID — only the Playwright sections

The agent will:

1. Fetch or load the transcript
2. Present topic clusters for confirmation
3. Ask where to save (project vs personal)
4. Write `SKILL.md` and `reference.md`

### Update an existing skill

> Update `@checkly` from this YouTube link — DNS section only

The agent reads the existing skill, presents a merge plan (NEW / ENRICH / SKIP / CONFLICT), and merges delta content.

### Multi-source

> Create a Playwright skill from this YouTube link AND our Meet recording (`sprint.vtt`)

## Supported sources

| Source | Auto-fetch | How to provide |
|--------|------------|----------------|
| YouTube | Yes | URL or 11-char video ID |
| Google Meet | No | `.sbv` file or pasted notes |
| Zoom | No | `.vtt` from cloud recording |
| Microsoft Teams | No | `.vtt` from meeting recap |
| Loom | No | `.txt` export or paste |
| Vimeo | No | `.vtt` captions |
| Meeting notes | No | Otter, Fireflies, Grain exports |
| Pasted text | N/A | Paste in chat |

Export guides: [providers.md](providers.md)

## Files

```
video-to-skill/
├── SKILL.md                  # Main workflow and agent instructions
├── providers.md              # Per-platform export guides
├── skill-output-template.md  # Template for generated SKILL.md
├── reference-template.md     # Template for generated reference.md
└── README.md                 # This file
```

## Example output

See the [checkly](../checkly/) skill — generated from a YouTube webinar using this workflow.

## License

Use and adapt freely.
