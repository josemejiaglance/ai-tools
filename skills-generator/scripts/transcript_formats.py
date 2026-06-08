"""Parse subtitle and plain-text files into normalized transcript segments."""

from __future__ import annotations

import re
from pathlib import Path


def parse_timestamp(value: str) -> float:
    """Parse VTT/SRT/SBV timestamp to seconds."""
    value = value.strip().replace(",", ".")
    parts = value.split(":")
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    if len(parts) == 2:
        minutes, seconds = parts
        return int(minutes) * 60 + float(seconds)
    return float(value)


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
        last = segments[-1]
        last_end = last["start"] + last["duration"]
        sections.append(
            {
                "start": current_start,
                "end": last_end,
                "timestamp": format_timestamp(current_start),
                "preview": " ".join(current_text)[:280],
            }
        )

    return sections


def finalize_transcript(
    *,
    source: str,
    segments: list[dict],
    title: str | None = None,
    url: str | None = None,
    language: str | None = None,
    input_path: str | None = None,
) -> dict:
    duration = 0.0
    if segments:
        last = segments[-1]
        duration = last["start"] + last["duration"]

    payload: dict = {
        "source": source,
        "title": title,
        "url": url,
        "language": language,
        "duration_seconds": duration,
        "duration": format_timestamp(duration),
        "segment_count": len(segments),
        "segments": segments,
        "sections": build_sections(segments),
    }
    if input_path:
        payload["input_path"] = input_path
    return payload


def _append_segment(
    segments: list[dict], start: float, end: float, text: str
) -> None:
    cleaned = " ".join(text.split())
    if not cleaned:
        return
    duration = max(end - start, 0.01)
    segments.append({"text": cleaned, "start": start, "duration": duration})


def parse_vtt(content: str) -> list[dict]:
    segments: list[dict] = []
    blocks = re.split(r"\n\s*\n", content.strip())
    time_pattern = re.compile(
        r"(\d{1,2}:\d{2}(?::\d{2})?(?:\.\d{1,3})?)\s*-->\s*"
        r"(\d{1,2}:\d{2}(?::\d{2})?(?:\.\d{1,3})?)"
    )

    for block in blocks:
        if block.startswith("WEBVTT") or block.startswith("NOTE"):
            continue
        match = time_pattern.search(block)
        if not match:
            continue
        start = parse_timestamp(match.group(1))
        end = parse_timestamp(match.group(2))
        text_lines = block[match.end() :].strip().splitlines()
        text = " ".join(
            line.strip()
            for line in text_lines
            if line.strip() and not line.startswith("NOTE")
        )
        text = re.sub(r"<[^>]+>", "", text)
        _append_segment(segments, start, end, text)

    return segments


def parse_srt(content: str) -> list[dict]:
    segments: list[dict] = []
    blocks = re.split(r"\n\s*\n", content.strip())
    time_pattern = re.compile(
        r"(\d{1,2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{1,2}:\d{2}:\d{2},\d{3})"
    )

    for block in blocks:
        match = time_pattern.search(block)
        if not match:
            continue
        start = parse_timestamp(match.group(1))
        end = parse_timestamp(match.group(2))
        text_lines = block[match.end() :].strip().splitlines()
        text = " ".join(line.strip() for line in text_lines if line.strip())
        _append_segment(segments, start, end, text)

    return segments


def parse_sbv(content: str) -> list[dict]:
    """Parse YouTube/Google .sbv subtitle format."""
    segments: list[dict] = []
    blocks = re.split(r"\n\s*\n", content.strip())
    time_pattern = re.compile(
        r"(\d{1,2}:\d{2}(?::\d{2})?(?:\.\d{1,3})?),"
        r"(\d{1,2}:\d{2}(?::\d{2})?(?:\.\d{1,3})?)"
    )

    for block in blocks:
        match = time_pattern.search(block)
        if not match:
            continue
        start = parse_timestamp(match.group(1))
        end = parse_timestamp(match.group(2))
        text = block[match.end() :].strip()
        _append_segment(segments, start, end, text)

    return segments


TIMESTAMP_LINE = re.compile(
    r"^(?:\[(?P<bracket>\d{1,2}:\d{2}(?::\d{2})?)\]|"
    r"(?P<plain>\d{1,2}:\d{2}(?::\d{2})?))\s*"
    r"(?:[-–—]|:)?\s*(?P<text>.+)$"
)


def parse_plain_text(content: str, words_per_minute: int = 150) -> list[dict]:
    """Parse plain text, using inline timestamps when present."""
    segments: list[dict] = []
    lines = content.splitlines()
    current_start: float | None = None
    current_text: list[str] = []

    def flush(end: float) -> None:
        nonlocal current_start, current_text
        if current_start is None or not current_text:
            current_text = []
            current_start = None
            return
        _append_segment(segments, current_start, end, " ".join(current_text))
        current_text = []
        current_start = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        match = TIMESTAMP_LINE.match(stripped)
        if match:
            ts = match.group("bracket") or match.group("plain")
            start = parse_timestamp(ts)
            if current_start is not None:
                flush(start)
            current_start = start
            current_text = [match.group("text")]
            continue

        if current_start is None:
            if segments:
                start = segments[-1]["start"] + segments[-1]["duration"]
            else:
                start = 0.0
            word_count = len(stripped.split())
            duration = max(word_count / words_per_minute * 60, 1.0)
            _append_segment(segments, start, start + duration, stripped)
        else:
            current_text.append(stripped)

    if current_start is not None and current_text:
        start = current_start
        word_count = len(" ".join(current_text).split())
        end = start + max(word_count / words_per_minute * 60, 1.0)
        flush(end)

    return segments


def detect_file_format(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".vtt":
        return "vtt"
    if suffix == ".srt":
        return "srt"
    if suffix == ".sbv":
        return "sbv"
    if suffix in {".txt", ".md", ".transcript"}:
        return "text"

    content = path.read_text(encoding="utf-8", errors="replace")[:500]
    if content.startswith("WEBVTT"):
        return "vtt"
    if re.search(r"\d{2}:\d{2}:\d{2},\d{3}\s*-->", content):
        return "srt"
    if re.search(r"\d:\d{2}(?::\d{2})?\.\d{1,3},\d:\d{2}", content):
        return "sbv"
    return "text"


def parse_file(
    path: Path,
    *,
    source: str | None = None,
    title: str | None = None,
) -> dict:
    content = path.read_text(encoding="utf-8", errors="replace")
    file_format = detect_file_format(path)
    if file_format == "vtt":
        segments = parse_vtt(content)
    elif file_format == "srt":
        segments = parse_srt(content)
    elif file_format == "sbv":
        segments = parse_sbv(content)
    else:
        segments = parse_plain_text(content)

    if not segments:
        raise ValueError(f"No transcript segments found in {path}")

    resolved_source = source or infer_source_from_path(path)
    resolved_title = title or path.stem.replace("_", " ").replace("-", " ").title()

    return finalize_transcript(
        source=resolved_source,
        segments=segments,
        title=resolved_title,
        url=str(path.resolve()),
        input_path=str(path.resolve()),
    )


def infer_source_from_path(path: Path) -> str:
    name = path.name.lower()
    if "meet" in name or "google" in name:
        return "google-meet"
    if "zoom" in name:
        return "zoom"
    if "teams" in name:
        return "teams"
    if "loom" in name:
        return "loom"
    if "otter" in name or "fireflies" in name:
        return "meeting-notes"
    return "file"


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


def merge_transcripts(transcripts: list[dict]) -> dict:
    if len(transcripts) == 1:
        return transcripts[0]

    total_segments = sum(t["segment_count"] for t in transcripts)
    return {
        "source": "multi",
        "title": " + ".join(t.get("title") or t.get("source", "source") for t in transcripts),
        "sources": transcripts,
        "source_count": len(transcripts),
        "segment_count": total_segments,
        "segments": [],
        "sections": [],
    }
