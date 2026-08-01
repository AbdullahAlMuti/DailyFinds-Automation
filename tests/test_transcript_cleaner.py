"""
Tests for Transcript Cleaner module (VTT/SRT parsing, deduplication, sponsorship detection).
"""

import os
import pytest
from scripts.transcript_cleaner import clean_vtt_or_srt, detect_segments, process_and_save_transcript


def test_clean_vtt_parsing():
    vtt_content = """WEBVTT
Kind: captions

00:00:00.000 --> 00:00:02.500
<c.colorFFF>Welcome back to</c> DailyFindz channel.

00:00:02.500 --> 00:00:05.000
Today we are going to look at kitchen organization.
"""
    clean_text, segments = clean_vtt_or_srt(vtt_content)
    assert "Welcome back to DailyFindz channel." in clean_text
    assert "Today we are going to look at kitchen organization." in clean_text
    assert len(segments) == 2
    assert segments[0]["timestamp"] == "00:00:00.000"


def test_deduplicate_scrolling_captions():
    vtt_content = """00:00:00.000 --> 00:00:02.000
Kitchen organization tips.

00:00:02.000 --> 00:00:04.000
Kitchen organization tips.
"""
    clean_text, segments = clean_vtt_or_srt(vtt_content)
    assert clean_text.count("Kitchen organization tips.") == 1


def test_detect_sponsorship_and_intros():
    sample_text = "Welcome back to our channel. Today we are exploring organization. This video is sponsored by NordVPN. Thanks for watching and don't forget to subscribe."
    detected = detect_segments(sample_text)
    assert len(detected["intros"]) > 0
    assert len(detected["sponsorships"]) > 0
    assert len(detected["outros"]) > 0


def test_process_and_save_transcript(tmp_path):
    out_dir = str(tmp_path)
    meta = {"tier": "Tier 1 - Unit Test", "is_machine_generated": False}
    raw_vtt = "WEBVTT\n\n00:00:00.000 --> 00:00:02.000\nTesting clean process."

    res = process_and_save_transcript(raw_vtt, out_dir, meta)

    assert os.path.exists(res["clean_text"])
    assert os.path.exists(res["timestamped_md"])
    assert os.path.exists(res["metadata_json"])

    with open(res["clean_text"], "r", encoding="utf-8") as f:
        assert f.read().strip() == "Testing clean process."
