"""
Main CLI Entrypoint for YouTube-to-WordPress SEO Agent.
Commands:
  validate        - Validates job configuration YAML against schema and environment.
  prepare         - Scaffolds package directory, extracts video metadata, and acquires transcript.
  check           - Runs blocking and warning quality gate checks on package.
  wordpress-test  - Tests WordPress REST API connectivity and authentication.
  wordpress-draft - Creates WordPress post draft from package.
  wordpress-publish - Publishes post if all safety tri-locks pass.
"""

import sys
import os
import re
import argparse
import json
import yaml
from typing import Dict, Any

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.utilities import (
    logger,
    setup_logger,
    load_yaml_config,
    validate_job_config,
    generate_slug
)
from scripts.youtube_source import extract_video_id, fetch_video_metadata, save_metadata
from scripts.transcript import acquire_transcript
from scripts.transcript_cleaner import process_and_save_transcript
from scripts.content_package import init_content_package, save_resolved_job, load_package_metadata
from scripts.quality_checker import evaluate_quality
from scripts.wordpress_client import WordPressClient, WordPressAPIError
from scripts.wordpress_test import test_connection

setup_logger()


def command_validate(args: argparse.Namespace) -> None:
    """Handles 'validate' command."""
    logger.info(f"Validating job file: {args.job}")
    config = load_yaml_config(args.job)
    validate_job_config(config)
    print("[OK] Job configuration is valid.")


def command_prepare(args: argparse.Namespace) -> None:
    """Handles 'prepare' command."""
    logger.info(f"Preparing package for job file: {args.job}")
    config = load_yaml_config(args.job)
    validate_job_config(config)

    video_url = config["youtube_url"]
    video_id = extract_video_id(video_url)

    # Initialize package directory
    base_out = os.getenv("OUTPUT_DIRECTORY", "outputs")
    package_dir = init_content_package(video_id, base_output_dir=base_out)

    # Fetch & save metadata
    meta = fetch_video_metadata(video_url)
    save_metadata(meta, os.path.join(package_dir, "source", "metadata.json"))

    # Acquire & clean transcript
    if args.dry_run:
        logger.info("[DRY RUN] Creating mock transcript artifacts...")
        raw_text = f"Mock transcript for video {video_id}. Today we are demonstrating kitchen organization techniques."
        ts_meta = {"tier": "Tier 1 - Mock Dry Run", "is_machine_generated": False}
    else:
        raw_text, ts_meta = acquire_transcript(video_id, video_url, package_dir, config.get("transcription", {}))

    process_and_save_transcript(raw_text, os.path.join(package_dir, "transcript"), ts_meta)
    save_resolved_job(package_dir, config)

    print(f"[OK] Content package prepared successfully at: {package_dir}")


def command_check(args: argparse.Namespace) -> None:
    """Handles 'check' command."""
    package_dir = os.path.abspath(args.package)
    logger.info(f"Evaluating quality gates for package: {package_dir}")

    job_file = os.path.join(package_dir, "job-resolved.yaml")
    job_config = load_yaml_config(job_file) if os.path.exists(job_file) else {}

    report = evaluate_quality(package_dir, job_config)
    if report["passed"]:
        print(f"[OK] Quality validation PASSED. (Word count: {report['word_count']}, Warnings: {len(report['warnings'])})")
    else:
        print(f"[FAIL] Quality validation FAILED with {len(report['blocking_failures'])} blocking errors.")
        for f in report["blocking_failures"]:
            print(f"   - {f}")
        sys.exit(1)


def command_wordpress_draft(args: argparse.Namespace, publish_intent: bool = False) -> None:
    """Handles 'wordpress-draft' and 'wordpress-publish' commands."""
    package_dir = os.path.abspath(args.package)
    logger.info(f"Processing WordPress post creation for package: {package_dir}")

    meta = load_package_metadata(package_dir)
    job_config = meta.get("job", {})

    art_html_path = os.path.join(package_dir, "article", "article.html")
    art_md_path = os.path.join(package_dir, "article", "article.md")

    if not os.path.exists(art_html_path):
        logger.error(f"Missing required article HTML file: {art_html_path}")
        sys.exit(1)

    with open(art_html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Extract title, slug, excerpt from markdown if present
    title = meta.get("source", {}).get("title", f"Guide: {meta.get('source', {}).get('video_id')}")
    slug = generate_slug(title)
    excerpt = "Practical guide and insights from DailyFindz."

    if os.path.exists(art_md_path):
        with open(art_md_path, "r", encoding="utf-8") as f:
            md_text = f.read()
        title_match = re.search(r'^#\s+(.+)$', md_text, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()
            slug = generate_slug(title)
        excerpt_match = re.search(r'\*\*Meta Description\*\*:\s*(.+)$', md_text, re.MULTILINE)
        if excerpt_match:
            excerpt = excerpt_match.group(1).strip()

    category_name = job_config.get("wordpress", {}).get("category", "Home & Kitchen")
    tag_names = job_config.get("wordpress", {}).get("tags", ["DailyFindz"])

    requested_status = "publish" if publish_intent else "draft"
    allow_publish_flag = getattr(args, "allow_publish", False)

    if args.dry_run:
        print("=" * 60)
        print(" [DRY RUN MODE] - WordPress Operation Simulated")
        print("=" * 60)
        print(f"Title:            {title}")
        print(f"Slug:             {slug}")
        print(f"Category:         {category_name}")
        print(f"Tags:             {tag_names}")
        print(f"Requested Status: {requested_status}")
        print(f"Allow Publish:    {allow_publish_flag}")
        print("Dry run completed cleanly. No HTTP calls were made to WordPress.")
        return

    # Real WordPress Execution
    client = WordPressClient()

    # Duplicate search
    dup = client.search_duplicate_post(slug, title)
    dup_policy = job_config.get("publishing", {}).get("duplicate_policy", "stop")
    if dup:
        if dup_policy == "stop":
            logger.error(f"Duplicate post found (Post ID: {dup['id']}, Slug: '{slug}'). Policy is 'stop'. Aborting.")
            sys.exit(1)

    # Category & Tag setup
    cat_id = client.get_or_create_category(category_name)
    tag_ids = client.get_or_create_tags(tag_names)

    # Upload Featured Image if available
    featured_media_id = None
    manifest_path = os.path.join(package_dir, "images", "image-manifest.json")
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        featured_entry = next((img for img in manifest if img.get("placement") == "featured"), None)
        if featured_entry and os.path.exists(featured_entry.get("file_path", "")):
            media_res = client.upload_media(
                file_path=featured_entry["file_path"],
                alt_text=featured_entry.get("alt_text", ""),
                title=title
            )
            featured_media_id = media_res.get("id")

    # Post Creation
    post = client.create_post(
        title=title,
        content_html=html_content,
        slug=slug,
        excerpt=excerpt,
        category_id=cat_id,
        tag_ids=tag_ids,
        featured_media_id=featured_media_id,
        requested_status=requested_status,
        allow_publish_flag=allow_publish_flag
    )

    print(f"[OK] WordPress Post Created Successfully!")
    print(f"   - Post ID:   {post['id']}")
    print(f"   - Status:    {post['status']}")
    print(f"   - Edit Link: {client.base_url}/wp-admin/post.php?post={post['id']}&action=edit")


def main() -> None:
    parser = argparse.ArgumentParser(description="YouTube-to-WordPress SEO Agent CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # validate
    val_parser = subparsers.add_parser("validate", help="Validate job YAML configuration")
    val_parser.add_argument("--job", required=True, help="Path to job YAML file")

    # prepare
    prep_parser = subparsers.add_parser("prepare", help="Scaffold package, extract metadata, and acquire transcript")
    prep_parser.add_argument("--job", required=True, help="Path to job YAML file")
    prep_parser.add_argument("--dry-run", action="store_true", help="Perform dry run without network calls")

    # check
    check_parser = subparsers.add_parser("check", help="Run quality check on package")
    check_parser.add_argument("--package", required=True, help="Path to package directory")

    # wordpress-test
    subparsers.add_parser("wordpress-test", help="Test WordPress REST API credentials")

    # wordpress-draft
    draft_parser = subparsers.add_parser("wordpress-draft", help="Create WordPress post draft")
    draft_parser.add_argument("--package", required=True, help="Path to package directory")
    draft_parser.add_argument("--dry-run", action="store_true", help="Perform dry run without updating WordPress")

    # wordpress-publish
    pub_parser = subparsers.add_parser("wordpress-publish", help="Publish WordPress post if safety locks pass")
    pub_parser.add_argument("--package", required=True, help="Path to package directory")
    pub_parser.add_argument("--allow-publish", action="store_true", help="Explicit CLI authorization for publication")
    pub_parser.add_argument("--dry-run", action="store_true", help="Perform dry run without updating WordPress")

    args = parser.parse_args()

    if args.command == "validate":
        command_validate(args)
    elif args.command == "prepare":
        command_prepare(args)
    elif args.command == "check":
        command_check(args)
    elif args.command == "wordpress-test":
        success = test_connection()
        sys.exit(0 if success else 1)
    elif args.command == "wordpress-draft":
        command_wordpress_draft(args, publish_intent=False)
    elif args.command == "wordpress-publish":
        command_wordpress_draft(args, publish_intent=True)


if __name__ == "__main__":
    main()
