# Transcript Scripts

Python utilities for loading and normalizing transcripts used by the [video-to-skill](../.cursor/skills/video-to-skill/SKILL.md) workflow.

Run all commands from the `skills-generator/` directory.

## Setup

```bash
python3 -m pip install -r requirements.txt
```

## load_transcript.py

Unified entry point for all transcript sources. Outputs normalized JSON with segments, timestamps, and section summaries.

### YouTube

```bash
# Fetch English transcript
python3 scripts/load_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID" -o transcript.json

# List available languages
python3 scripts/load_transcript.py "VIDEO_ID" --list-only

# Fetch with language fallback
python3 scripts/load_transcript.py "VIDEO_ID" --languages es en -o transcript.json
```

### Subtitle and caption files

Supports `.vtt`, `.srt`, `.sbv`, and plain `.txt`:

```bash
python3 scripts/load_transcript.py meeting.vtt \
  --source google-meet \
  --title "Architecture sync" \
  -o transcript.json
```

Set `--source` when the filename does not hint at the platform (`google-meet`, `zoom`, `teams`, `loom`, `vimeo`, `paste`).

### Pasted text

```bash
python3 scripts/load_transcript.py "Speaker: Hello world at 0:05..." --source paste -o transcript.json
```

### Multiple sources

```bash
python3 scripts/load_transcript.py "https://youtu.be/ID" meeting.vtt notes.txt --merge -o transcript.json
```

Merged output has `"source": "multi"` and a `sources` array with per-source payloads.

### Time filtering

```bash
python3 scripts/load_transcript.py "VIDEO_ID" --start 300 --end 720 -o filtered.json
```

`--start` and `--end` are in seconds. For multi-source inputs, filter each source independently before merging.

## fetch_transcript.py

Legacy YouTube-only fetcher. Prefer `load_transcript.py` for new usage.

```bash
python3 scripts/fetch_transcript.py "https://youtu.be/VIDEO_ID" -o transcript.json
python3 scripts/fetch_transcript.py "VIDEO_ID" --list-only
python3 scripts/fetch_transcript.py "VIDEO_ID" --start 120 --end 600 -o clip.json
```

## transcript_formats.py

Internal module — parsers for VTT, SRT, SBV, and plain text. Not invoked directly; used by `load_transcript.py`.

## Output format

All loaders produce JSON with this shape:

```json
{
  "source": "youtube",
  "title": "Video title",
  "url": "https://www.youtube.com/watch?v=...",
  "duration_seconds": 3600.0,
  "duration": "60:00",
  "segment_count": 1200,
  "segments": [
    { "text": "Hello world", "start": 0.0, "duration": 2.5 }
  ],
  "sections": [
    { "start": 0.0, "end": 120.0, "timestamp": "0:00", "preview": "..." }
  ]
}
```

Multi-source payloads add `"sources": [...]` instead of top-level segments.

## Common errors

| Error | Fix |
|-------|-----|
| Transcripts disabled (YouTube) | Paste transcript manually or use `--list-only` to check languages |
| No transcript for language | Run `--list-only`, then `--languages <code> en` |
| Meet/Zoom/Teams URL only | Export captions from the platform; URLs cannot be auto-fetched |
| Unrecognized file format | Provide `.vtt`, `.srt`, `.sbv`, or plain text |

Platform-specific export steps: [providers.md](../.cursor/skills/video-to-skill/providers.md)
