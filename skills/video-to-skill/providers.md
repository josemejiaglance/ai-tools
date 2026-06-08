# Transcript Providers

How to load content for **video-to-skill**. Use `scripts/load_transcript.py` as the single entry point.

## Unified loader

```bash
# YouTube (auto-fetch)
python3 scripts/load_transcript.py "<youtube-url>" -o /tmp/transcript.json

# Subtitle or text file
python3 scripts/load_transcript.py meeting.vtt --source google-meet --title "Sprint review" -o /tmp/transcript.json

# Multiple sources (merged)
python3 scripts/load_transcript.py "<youtube-url>" meeting.vtt notes.txt --merge -o /tmp/transcript.json

# Time range filter (seconds)
python3 scripts/load_transcript.py "<youtube-url>" --start 300 --end 720 -o /tmp/transcript-filtered.json
```

Supported file formats: `.vtt`, `.srt`, `.sbv`, `.txt`, `.md`

Plain text with inline timestamps: `[00:12:34] Speaker: text` or `00:12:34 text`

---

## Provider matrix

| Provider | Auto-fetch URL? | Typical export | `--source` label |
|----------|-----------------|----------------|------------------|
| **YouTube** | Yes | — | `youtube` (automatic) |
| **Google Meet** | No | .sbv from Drive, copy from Transcripts panel, Gemini notes | `google-meet` |
| **Zoom** | No | .vtt from cloud recording | `zoom` |
| **Microsoft Teams** | No | .vtt from meeting recap / Stream | `teams` |
| **Loom** | No | Copy transcript from video page | `loom` |
| **Vimeo** | No | .vtt download (if captions enabled) | `vimeo` |
| **Otter / Fireflies / Grain** | No | .txt or .srt export | `meeting-notes` |
| **Conference talk** | No | .srt from event site | `conference` |
| **Pasted text** | N/A | User pastes in chat | `paste` |
| **Local file** | N/A | Any supported format | inferred from filename |

When auto-fetch is unavailable, show export steps and ask the user to provide a file or paste.

---

## Export guides

### Google Meet

1. **During/after meeting:** Activities (right panel) → Transcripts → open → copy or download
2. **Recorded to Drive:** Open recording in Drive → ⋮ → Download → Subtitles (.sbv)
3. **Gemini notes:** Google Docs meeting notes → copy text (timestamps may be inline)

```bash
python3 scripts/load_transcript.py ~/Downloads/meeting.sbv --source google-meet --title "Architecture sync" -o /tmp/transcript.json
```

### Zoom

1. Zoom web portal → Recordings → select recording → Download → **Audio transcript (.vtt)**
2. Or copy transcript text from the recording page

```bash
python3 scripts/load_transcript.py ~/Downloads/recording.vtt --source zoom -o /tmp/transcript.json
```

### Microsoft Teams

1. Teams → meeting chat → **Transcript** tab → download .vtt (when available)
2. Or Teams Stream / meeting recap → Export transcript

```bash
python3 scripts/load_transcript.py ~/Downloads/teams-meeting.vtt --source teams -o /tmp/transcript.json
```

### Loom

1. Open video → **Transcript** tab → Select all → copy
2. Save as `.txt` or paste directly

```bash
python3 scripts/load_transcript.py ~/Downloads/loom-transcript.txt --source loom --title "Demo walkthrough" -o /tmp/transcript.json
```

### Vimeo

1. Video page → Settings → Download → Captions (.vtt) — only if uploader enabled captions
2. Or paste transcript if shown on page

### Otter.ai / Fireflies / Grain

1. Export as `.txt` or `.srt` from the meeting dashboard
2. Use `--source meeting-notes` and set `--title`

### Pasted transcript (no file)

If the user pastes text in chat, the agent normalizes it to JSON directly (same segment shape as the loader). Save as `/tmp/transcript.json`.

---

## Multi-source workflow

When the user provides **multiple sources** for one skill:

1. Load each input (URL, file, or paste)
2. Merge with `--merge` or load sequentially and combine
3. Cluster topics **across all sources** in Step 3
4. List every source in the skill's `## Source` section
5. On **update**, append new sources — never remove prior entries

Example merged payload shape:

```json
{
  "source": "multi",
  "source_count": 2,
  "sources": [
    { "source": "youtube", "title": "...", "segments": [...] },
    { "source": "google-meet", "title": "Sprint review", "segments": [...] }
  ]
}
```

When analyzing, treat each source's segments independently for timestamps; prefix subcategory notes with source name when times aren't comparable.

---

## Normalized JSON shape

Every provider outputs:

```json
{
  "source": "google-meet",
  "title": "Sprint review",
  "url": "/path/to/file.vtt",
  "duration_seconds": 3600,
  "duration": "60:00",
  "segment_count": 420,
  "segments": [
    { "text": "...", "start": 0.0, "duration": 2.5 }
  ],
  "sections": [
    { "start": 0, "end": 120, "timestamp": "0:00", "preview": "..." }
  ]
}
```

YouTube payloads include additional fields (`video_id`, `language`, `available_transcripts`).

---

## Legacy YouTube-only script

`scripts/fetch_transcript.py` still works for YouTube. Prefer `load_transcript.py` for all new usage.
