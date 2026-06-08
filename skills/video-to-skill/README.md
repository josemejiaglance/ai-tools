# Video to Skill

An [Agent Skill](https://agentskills.io) that turns video and transcript content into reusable skills — or updates existing ones. Works with Cursor, Codex, Claude Code, and any agent that supports the open standard.

## Install

```bash
npx skills add josemejiaglance/ai-tools@video-to-skill
```

The install bundles `scripts/` and `requirements.txt` for transcript loading.

```bash
# Global install
npx skills add josemejiaglance/ai-tools@video-to-skill -g -y
```

## Python setup

```bash
cd .agents/skills/video-to-skill   # or your install path
python3 -m pip install -r requirements.txt
```

## Usage

```
@video-to-skill
```

### Create a skill

> Create a skill from https://www.youtube.com/watch?v=VIDEO_ID — only the Playwright sections

### Update an existing skill

> Update `@checkly` from this YouTube link — DNS section only

### Multi-source

> Create a Playwright skill from this YouTube link AND our Meet recording (`sprint.vtt`)

## Supported sources

YouTube (auto-fetch), Google Meet, Zoom, Teams, Loom, Vimeo, meeting note exports, and pasted text.

Export guides: [providers.md](providers.md)

## Example output

See the [checkly](../checkly/) skill — generated using this workflow.
