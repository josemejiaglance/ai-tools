#!/usr/bin/env python3
"""Fetch a YouTube video transcript with timestamps and section summaries."""

from __future__ import annotations

import argparse
import json
import re
import sys
from urllib.error import URLError
from urllib.request import urlopen

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)


def extract_video_id(url_or_id: str) -> str:
    value = url_or_id.strip()
    patterns = [
        r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/shorts/)([a-zA-Z0-9_-]{11})",
        r"^([a-zA-Z0-9_-]{11})$",
    ]
    for pattern in patterns:
        match = re.search(pattern, value)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract a YouTube video ID from: {url_or_id}")


def fetch_video_title(video_id: str) -> str | None:
    try:
        with urlopen(
            f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json",
            timeout=10,
        ) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data.get("title")
    except (URLError, TimeoutError, json.JSONDecodeError, KeyError):
        return None


def format_timestamp(seconds: float) -> str:
    total = int(seconds)
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def build_sections(segments: list[dict], interval_seconds: int = 120) -> list[dict]:
    if not segments:
        return []

    sections: list[dict] = []
    current_start = segments[0]["start"]
    current_text: list[str] = []

    for segment in segments:
        if segment["start"] - current_start >= interval_seconds and current_text:
            sections.append(
                {
                    "start": current_start,
                    "end": segment["start"],
                    "timestamp": format_timestamp(current_start),
                    "preview": " ".join(current_text)[:280],
                }
            )
            current_start = segment["start"]
            current_text = []
        current_text.append(segment["text"])

    if current_text:
        last_end = segments[-1]["start"] + segments[-1]["duration"]
        sections.append(
            {
                "start": current_start,
                "end": last_end,
                "timestamp": format_timestamp(current_start),
                "preview": " ".join(current_text)[:280],
            }
        )

    return sections


def list_available_transcripts(video_id: str) -> list[dict]:
    api = YouTubeTranscriptApi()
    transcript_list = api.list(video_id)
    return [
        {
            "language": transcript.language,
            "language_code": transcript.language_code,
            "is_generated": transcript.is_generated,
            "is_translatable": transcript.is_translatable,
        }
        for transcript in transcript_list
    ]


def fetch_transcript(video_id: str, languages: list[str] | None = None) -> dict:
    api = YouTubeTranscriptApi()
    fetched = api.fetch(video_id, languages=languages or ["en"])
    segments = fetched.to_raw_data()

    duration = 0.0
    if segments:
        last = segments[-1]
        duration = last["start"] + last["duration"]

    return {
        "source": "youtube",
        "video_id": video_id,
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "title": fetch_video_title(video_id),
        "language": fetched.language,
        "language_code": fetched.language_code,
        "is_generated": fetched.is_generated,
        "duration_seconds": duration,
        "duration": format_timestamp(duration),
        "segment_count": len(segments),
        "segments": segments,
        "sections": build_sections(segments),
        "available_transcripts": list_available_transcripts(video_id),
    }


def filter_by_time_range(
    data: dict, start_seconds: float | None, end_seconds: float | None
) -> dict:
    if start_seconds is None and end_seconds is None:
        return data

    filtered = []
    for segment in data["segments"]:
        segment_end = segment["start"] + segment["duration"]
        if start_seconds is not None and segment_end < start_seconds:
            continue
        if end_seconds is not None and segment["start"] > end_seconds:
            continue
        filtered.append(segment)

    result = dict(data)
    result["segments"] = filtered
    result["sections"] = build_sections(filtered)
    result["filtered_range"] = {
        "start_seconds": start_seconds,
        "end_seconds": end_seconds,
        "start": format_timestamp(start_seconds or 0),
        "end": format_timestamp(end_seconds or data["duration_seconds"]),
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch a YouTube transcript as JSON")
    parser.add_argument("url", help="YouTube URL or 11-character video ID")
    parser.add_argument(
        "--languages",
        nargs="+",
        default=["en"],
        help="Preferred transcript languages in priority order (default: en)",
    )
    parser.add_argument(
        "--start",
        type=float,
        default=None,
        help="Only include transcript from this timestamp in seconds",
    )
    parser.add_argument(
        "--end",
        type=float,
        default=None,
        help="Only include transcript up to this timestamp in seconds",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Write JSON output to this file instead of stdout",
    )
    parser.add_argument(
        "--list-only",
        action="store_true",
        help="List available transcripts without fetching content",
    )
    args = parser.parse_args()

    try:
        video_id = extract_video_id(args.url)
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1

    try:
        if args.list_only:
            payload = {
                "video_id": video_id,
                "title": fetch_video_title(video_id),
                "available_transcripts": list_available_transcripts(video_id),
            }
        else:
            payload = fetch_transcript(video_id, languages=args.languages)
            payload = filter_by_time_range(payload, args.start, args.end)
    except TranscriptsDisabled:
        error = "Transcripts are disabled for this video."
    except NoTranscriptFound:
        error = (
            "No transcript found for the requested languages. "
            "Run with --list-only to see available options."
        )
    except VideoUnavailable:
        error = "Video is unavailable."
    except Exception as exc:  # noqa: BLE001 - surface library errors to CLI
        error = str(exc)
    else:
        output = json.dumps(payload, indent=2, ensure_ascii=False)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as handle:
                handle.write(output)
            print(f"Wrote transcript to {args.output}")
        else:
            print(output)
        return 0

    print(json.dumps({"error": error, "video_id": video_id}), file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
