"""
Tests for Quality Checker module (blocking failures, placeholder detection, safety tri-lock).
"""

import os
import json
import pytest
from scripts.quality_checker import evaluate_quality


def test_quality_checker_missing_transcript(tmp_path):
    pkg_dir = str(tmp_path)
    job_config = {"content": {"minimum_words": 100}}

    report = evaluate_quality(pkg_dir, job_config)
    assert not report["passed"]
    assert any("Missing transcript" in f for f in report["blocking_failures"])


def test_quality_checker_placeholder_text_detected(tmp_path):
    pkg_dir = str(tmp_path)
    ts_dir = os.path.join(pkg_dir, "transcript")
    art_dir = os.path.join(pkg_dir, "article")
    img_dir = os.path.join(pkg_dir, "images")
    os.makedirs(ts_dir, exist_ok=True)
    os.makedirs(art_dir, exist_ok=True)
    os.makedirs(img_dir, exist_ok=True)

    # Valid transcript
    with open(os.path.join(ts_dir, "transcript-clean.txt"), "w", encoding="utf-8") as f:
        f.write("Word " * 150)

    # Article with placeholder text
    with open(os.path.join(art_dir, "article.md"), "w", encoding="utf-8") as f:
        f.write("# Sample Title\n\nThis is a sample article body with [TODO] placeholder text.\n" + ("Word " * 200))

    with open(os.path.join(art_dir, "article.html"), "w", encoding="utf-8") as f:
        f.write("<h1>Sample Title</h1><p>This is a sample article body with [TODO] placeholder text.</p>")

    # Mock featured image
    img_file = os.path.join(img_dir, "featured.webp")
    with open(img_file, "w") as f:
        f.write("fake image")

    manifest = [{"placement": "featured", "file_path": img_file, "alt_text": "Sample Alt"}]
    with open(os.path.join(img_dir, "image-manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f)

    job_config = {"content": {"minimum_words": 100}, "images": {"featured_image": True}}

    report = evaluate_quality(pkg_dir, job_config)
    assert not report["passed"]
    assert any("Placeholder text" in f for f in report["blocking_failures"])


def test_quality_checker_pass_clean_package(tmp_path):
    pkg_dir = str(tmp_path)
    ts_dir = os.path.join(pkg_dir, "transcript")
    art_dir = os.path.join(pkg_dir, "article")
    img_dir = os.path.join(pkg_dir, "images")
    os.makedirs(ts_dir, exist_ok=True)
    os.makedirs(art_dir, exist_ok=True)
    os.makedirs(img_dir, exist_ok=True)

    # Valid transcript
    with open(os.path.join(ts_dir, "transcript-clean.txt"), "w", encoding="utf-8") as f:
        f.write("Word " * 200)

    # Valid Article
    art_text = "# Clean Title\n\n**Meta Description**: This is a valid description that is long enough for testing.\n\n" + ("Clean word content. " * 50)
    with open(os.path.join(art_dir, "article.md"), "w", encoding="utf-8") as f:
        f.write(art_text)

    with open(os.path.join(art_dir, "article.html"), "w", encoding="utf-8") as f:
        f.write("<h1>Clean Title</h1><p>" + ("Clean word content. " * 50) + "</p>")

    # Mock featured image
    img_file = os.path.join(img_dir, "featured.webp")
    with open(img_file, "w") as f:
        f.write("fake image")

    manifest = [{"placement": "featured", "file_path": img_file, "alt_text": "Sample Alt"}]
    with open(os.path.join(img_dir, "image-manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f)

    job_config = {"content": {"minimum_words": 100}, "images": {"featured_image": True}}

    report = evaluate_quality(pkg_dir, job_config)
    assert report["passed"]
    assert len(report["blocking_failures"]) == 0
