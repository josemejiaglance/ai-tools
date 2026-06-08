# Transcript Scripts

Python utilities bundled with the video-to-skill skill. Run from the skill root directory (parent of `scripts/`).

## Setup

```bash
python3 -m pip install -r requirements.txt
```

## load_transcript.py

Unified entry point for all transcript sources. Outputs normalized JSON with segments, timestamps, and section summaries.

```bash
# YouTube
python3 scripts/load_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID" -o transcript.json

# Meeting caption file
python3 scripts/load_transcript.py meeting.vtt --source google-meet -o transcript.json

# Multiple sources
python3 scripts/load_transcript.py "https://youtu.be/ID" meeting.vtt --merge -o transcript.json

# Filter by time range (seconds)
python3 scripts/load_transcript.py "VIDEO_ID" --start 300 --end 720 -o filtered.json
```

See the [video-to-skill SKILL.md](../SKILL.md) for full usage. Platform export guides: [providers.md](../providers.md).
