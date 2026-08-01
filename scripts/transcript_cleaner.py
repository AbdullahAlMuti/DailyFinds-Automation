"""
Transcript Cleaner and Structurer.
Parses raw transcript files (VTT, SRT, TXT, JSON), removes subtitle markup and duplicate lines,
preserves timestamps, detects sponsorships & intro/outro sections, and generates clean artifacts.
"""

import re
import json
import os
import sys
from typing import Dict, Any, List, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.utilities import logger


def clean_vtt_or_srt(raw_content: str) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Parses VTT or SRT raw subtitle content.
    Returns a tuple of (clean_text, timestamped_segments).
    """
    lines = raw_content.splitlines()
    timestamped_segments = []
    clean_lines = []

    # Regex for timestamp lines (00:00:01.500 --> 00:00:04.200 or 00:01:15,000 --> 00:01:18,000)
    time_pattern = re.compile(r'(\d{2}:)?\d{2}:\d{2}[\.,]\d{3}\s*-->\s*(\d{2}:)?\d{2}:\d{2}[\.,]\d{3}')

    current_start = ""
    current_text_buf = []

    for line in lines:
        line_str = line.strip()

        # Skip headers, numbers, or empty lines
        if not line_str or line_str.startswith("WEBVTT") or line_str.startswith("NOTE") or line_str.isdigit():
            continue

        # Match timestamp
        time_match = time_pattern.search(line_str)
        if time_match:
            if current_start and current_text_buf:
                full_seg_text = " ".join(current_text_buf).strip()
                if full_seg_text:
                    timestamped_segments.append({"timestamp": current_start, "text": full_seg_text})
                current_text_buf = []

            # Extract start timestamp
            current_start = line_str.split("-->")[0].strip()
            continue

        # Remove inner subtitle tags like <c.colorFFF>, <b>, <i>, <font>
        line_clean = re.sub(r'<[^>]+>', '', line_str)
        line_clean = re.sub(r'&nbsp;', ' ', line_clean)

        if line_clean:
            current_text_buf.append(line_clean)

    # Flush last segment
    if current_start and current_text_buf:
        full_seg_text = " ".join(current_text_buf).strip()
        if full_seg_text:
            timestamped_segments.append({"timestamp": current_start, "text": full_seg_text})

    # Deduplicate overlapping caption lines
    deduped_segments = _deduplicate_caption_lines(timestamped_segments)
    clean_text = " ".join([seg["text"] for seg in deduped_segments])

    return clean_text, deduped_segments


def _deduplicate_caption_lines(segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Removes scrolling duplicate subtitle lines typical in auto-generated captions."""
    deduped = []
    last_text = ""

    for seg in segments:
        text = seg["text"].strip()
        if not text:
            continue
        # If line repeats previous phrase exactly or is substring of previous
        if text == last_text:
            continue
        if len(text) > 5 and text in last_text and len(last_text) - len(text) < 15:
            continue

        deduped.append(seg)
        last_text = text

    return deduped


def detect_segments(text: str) -> Dict[str, List[str]]:
    """
    Detects introductions, outros, and sponsorship segments in transcript text.
    """
    sponsorship_keywords = ["sponsor", "sponsored by", "thanks to", "use code", "check out the link in the description", "NordVPN", "Squarespace", "Audible"]
    intro_keywords = ["welcome back", "in this video", "today we are", "hey guys", "what's up"]
    outro_keywords = ["thanks for watching", "don't forget to subscribe", "leave a comment", "see you next time", "hit the bell icon"]

    sponsorships = []
    intros = []
    outros = []

    sentences = re.split(r'(?<=[.!?])\s+', text)
    for sentence in sentences:
        sentence_lower = sentence.lower()
        if any(kw in sentence_lower for kw in sponsorship_keywords):
            sponsorships.append(sentence)
        if any(kw in sentence_lower for kw in intro_keywords):
            intros.append(sentence)
        if any(kw in sentence_lower for kw in outro_keywords):
            outros.append(sentence)

    return {
        "intros": intros,
        "sponsorships": sponsorships,
        "outros": outros
    }


def process_and_save_transcript(
    raw_content: str,
    output_folder: str,
    acquisition_metadata: Dict[str, Any]
) -> Dict[str, str]:
    """
    Cleans transcript, builds timestamped markdown, detects segments, and writes all artifacts.
    Returns dict of paths created.
    """
    os.makedirs(output_folder, exist_ok=True)

    # Determine if raw content is VTT/SRT or plain text
    if "-->" in raw_content or "WEBVTT" in raw_content:
        clean_text, timestamped_segs = clean_vtt_or_srt(raw_content)
    else:
        clean_text = raw_content.strip()
        timestamped_segs = [{"timestamp": "00:00:00", "text": clean_text}]

    # Format timestamped markdown
    ts_lines = ["# Timestamped Transcript\n"]
    for seg in timestamped_segs:
        ts_lines.append(f"- **[{seg['timestamp']}]**: {seg['text']}")
    timestamped_md = "\n".join(ts_lines)

    # Segment detection
    detected = detect_segments(clean_text)

    # Write transcript-clean.txt
    clean_path = os.path.join(output_folder, "transcript-clean.txt")
    with open(clean_path, "w", encoding="utf-8") as f:
        f.write(clean_text)

    # Write transcript-timestamped.md
    ts_path = os.path.join(output_folder, "transcript-timestamped.md")
    with open(ts_path, "w", encoding="utf-8") as f:
        f.write(timestamped_md)

    # Write transcript-metadata.json
    metadata_summary = {
        **acquisition_metadata,
        "character_count": len(clean_text),
        "estimated_word_count": len(clean_text.split()),
        "detected_segments": detected
    }
    meta_path = os.path.join(output_folder, "transcript-metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata_summary, f, indent=2, ensure_ascii=False)

    logger.info(f"Transcript cleaning complete: {clean_path}")
    return {
        "clean_text": clean_path,
        "timestamped_md": ts_path,
        "metadata_json": meta_path
    }
