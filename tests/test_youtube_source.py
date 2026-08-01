"""
Tests for YouTube Source module (URL extraction, Video ID extraction, error handling).
"""

import pytest
from scripts.youtube_source import extract_video_id, fetch_video_metadata


def test_extract_video_id_valid_formats():
    assert extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert extract_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert extract_video_id("https://www.youtube.com/embed/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert extract_video_id("https://www.youtube.com/shorts/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ&feature=shared") == "dQw4w9WgXcQ"


def test_extract_video_id_invalid_formats():
    with pytest.raises(ValueError):
        extract_video_id("https://example.com/not-youtube")

    with pytest.raises(ValueError):
        extract_video_id("")

    with pytest.raises(ValueError):
        extract_video_id("https://youtube.com/watch?v=short")


def test_fetch_video_metadata_handles_exceptions(mocker=None):
    # Tests graceful offline/network failure handling
    meta = fetch_video_metadata("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert meta["video_id"] == "dQw4w9WgXcQ"
    assert "title" in meta
    assert "channel_name" in meta
