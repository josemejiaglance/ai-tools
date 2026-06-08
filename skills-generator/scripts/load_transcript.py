#!/usr/bin/env python3
"""Load transcripts from YouTube URLs, subtitle files, or plain text."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from transcript_formats import (
    filter_by_time_range,
    finalize_transcript,
    merge_transcripts,
    parse_file,
    parse_plain_text,
)

# Reuse YouTube fetcher from sibling module
from fetch_transcript import (
    extract_video_id,
    fetch_transcript as fetch_youtube_transcript,
    list_available_transcripts,
)


YOUTUBE_PATTERN = re.compile(
    r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/shorts/)"
    r"([a-zA-Z0-9_-]{11})"
    r"|^([a-zA-Z0-9_-]{11})$"
)

PROVIDER_URL_HINTS: dict[str, re.Pattern[str]] = {
    "google-meet": re.compile(r"meet\.google\.com", re.I),
    "zoom": re.compile(r"zoom\.us/(?:j|rec|meeting)", re.I),
    "teams": re.compile(r"teams\.(?:microsoft|live)\.com", re.I),
    "loom": re.compile(r"loom\.com/share/", re.I),
    "vimeo": re.compile(r"vimeo\.com/\d+", re.I),
}

EXPORT_GUIDANCE = {
    "google-meet": (
        "Google Meet has no public transcript API. Export captions:\n"
        "  1. Google Meet → Activities → Transcripts → copy or save\n"
        "  2. Google Drive recording → Download .sbv subtitles\n"
        "  3. Gemini meeting notes in Google Docs → paste as plain text\n"
        "Then: python3 scripts/load_transcript.py meeting.sbv --source google-meet -o /tmp/transcript.json"
    ),
    "zoom": (
        "Export Zoom cloud recording captions (.vtt) or copy transcript from the web portal.\n"
        "Then: python3 scripts/load_transcript.py recording.vtt --source zoom -o /tmp/transcript.json"
    ),
    "teams": (
        "Export Teams meeting transcript (.vtt) from the meeting recap or Stream.\n"
        "Then: python3 scripts/load_transcript.py meeting.vtt --source teams -o /tmp/transcript.json"
    ),
    "loom": (
        "Open Loom → Video → Transcript → copy text, or download if available.\n"
        "Then paste or save as .txt and run load_transcript.py on the file."
    ),
    "vimeo": (
        "Download .vtt from Vimeo video settings (if captions exist), or paste transcript.\n"
        "Then: python3 scripts/load_transcript.py captions.vtt --source vimeo -o /tmp/transcript.json"
    ),
}


def detect_input_kind(value: str) -> tuple[str, str | None]:
    stripped = value.strip()

    if YOUTUBE_PATTERN.search(stripped):
        return "youtube", stripped

    for provider, pattern in PROVIDER_URL_HINTS.items():
        if pattern.search(stripped):
            return provider, stripped

    path = Path(stripped)
    if path.exists() and path.is_file():
        return "file", str(path.resolve())

    if stripped.startswith(("http://", "https://")):
        return "url", stripped

    if "\n" in stripped or len(stripped.split()) > 30:
        return "text", stripped

    return "unknown", stripped


def load_youtube(
    url_or_id: str,
    languages: list[str] | None,
    list_only: bool,
) -> dict:
    video_id = extract_video_id(url_or_id)
    if list_only:
        from fetch_transcript import fetch_video_title

        return {
            "source": "youtube",
            "video_id": video_id,
            "title": fetch_video_title(video_id),
            "available_transcripts": list_available_transcripts(video_id),
        }
    return fetch_youtube_transcript(video_id, languages=languages)


def load_text(
    content: str,
    *,
    source: str,
    title: str | None,
    url: str | None,
) -> dict:
    segments = parse_plain_text(content)
    if not segments:
        raise ValueError("No transcript content found in pasted text.")
    return finalize_transcript(
        source=source,
        segments=segments,
        title=title or "Pasted transcript",
        url=url,
    )


def load_input(
    value: str,
    *,
    source: str | None,
    title: str | None,
    languages: list[str] | None,
    list_only: bool,
) -> dict:
    kind, payload = detect_input_kind(value)

    if kind == "youtube":
        return load_youtube(payload or value, languages, list_only)

    if kind == "file":
        return parse_file(Path(payload), source=source, title=title)

    if kind == "text":
        return load_text(
            payload or value,
            source=source or "paste",
            title=title,
            url=None,
        )

    if kind in EXPORT_GUIDANCE:
        raise RuntimeError(
            f"{kind} URLs cannot be fetched automatically.\n\n{EXPORT_GUIDANCE[kind]}"
        )

    raise ValueError(
        f"Unrecognized input: {value}\n"
        "Provide a YouTube URL, subtitle file (.vtt/.srt/.sbv/.txt), "
        "or paste transcript text."
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Load transcript(s) from YouTube, files, or pasted text as JSON"
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        help="YouTube URL, file path, or pasted transcript text",
    )
    parser.add_argument(
        "--source",
        help="Override source label (google-meet, zoom, teams, loom, vimeo, paste, …)",
    )
    parser.add_argument("--title", help="Override transcript title")
    parser.add_argument(
        "--languages",
        nargs="+",
        default=["en"],
        help="Preferred YouTube transcript languages (default: en)",
    )
    parser.add_argument("--start", type=float, default=None, help="Start time in seconds")
    parser.add_argument("--end", type=float, default=None, help="End time in seconds")
    parser.add_argument("-o", "--output", help="Write JSON to this file")
    parser.add_argument(
        "--list-only",
        action="store_true",
        help="List YouTube transcript options without fetching content",
    )
    parser.add_argument(
        "--merge",
        action="store_true",
        help="Merge multiple inputs into one multi-source payload",
    )
    args = parser.parse_args()

    loaded: list[dict] = []
    for item in args.inputs:
        try:
            data = load_input(
                item,
                source=args.source,
                title=args.title,
                languages=args.languages,
                list_only=args.list_only,
            )
        except Exception as exc:  # noqa: BLE001
            print(json.dumps({"error": str(exc), "input": item}), file=sys.stderr)
            return 1

        if not args.list_only:
            data = filter_by_time_range(data, args.start, args.end)
        loaded.append(data)

    payload = merge_transcripts(loaded) if args.merge or len(loaded) > 1 else loaded[0]

    output = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(output)
        print(f"Wrote transcript to {args.output}")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
