"""
Utility functions for YouTube-to-WordPress SEO Agent.
Handles logging setup with secret redaction, configuration parsing/validation,
HTML sanitization, and path helpers.
"""

import os
import re
import logging
from typing import Dict, Any, Optional
import yaml
from dotenv import load_dotenv
try:
    import bleach
    HAS_BLEACH = True
except ImportError:
    HAS_BLEACH = False

from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()


class SecretRedactingFormatter(logging.Formatter):
    """Logging formatter that redacts sensitive information such as application passwords."""

    REDACT_PATTERNS = [
        (re.compile(r'(WP_APP_PASSWORD=)([^\s&"\']+)', re.IGNORECASE), r'\1[REDACTED]'),
        (re.compile(r'(Basic\s+)([A-Za-z0-9+/=]{10,})'), r'\1[REDACTED]'),
        (re.compile(r'("wp_app_password"\s*:\s*")[^"]+(")', re.IGNORECASE), r'\1[REDACTED]\2'),
        (re.compile(r'("password"\s*:\s*")[^"]+(")', re.IGNORECASE), r'\1[REDACTED]\2'),
    ]

    def format(self, record: logging.LogRecord) -> str:
        formatted = super().format(record)
        app_password = os.getenv("WP_APP_PASSWORD", "")
        if app_password and len(app_password.strip()) > 3:
            formatted = formatted.replace(app_password, "[REDACTED]")
            # Also mask space-removed version if present
            formatted = formatted.replace(app_password.replace(" ", ""), "[REDACTED]")
        for pattern, replacement in self.REDACT_PATTERNS:
            formatted = pattern.sub(replacement, formatted)
        return formatted


def setup_logger(name: str = "youtube_seo_agent", log_level: Optional[str] = None) -> logging.Logger:
    """Configures and returns a logger with secret redaction enabled."""
    level_str = log_level or os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_str, logging.INFO)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        formatter = SecretRedactingFormatter("[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s")
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


logger = setup_logger()


def load_yaml_config(file_path: str) -> Dict[str, Any]:
    """Loads and returns a YAML configuration file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Configuration file not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def validate_job_config(config: Dict[str, Any]) -> None:
    """Validates the job YAML structure and throws ValueError if invalid."""
    if not config.get("youtube_url"):
        raise ValueError("Job configuration missing required field: 'youtube_url'")

    content = config.get("content", {})
    if not isinstance(content, dict):
        raise ValueError("Job 'content' section must be a dictionary")

    min_words = content.get("minimum_words", 3000)
    max_words = content.get("maximum_words", 4500)
    if min_words > max_words:
        raise ValueError(f"minimum_words ({min_words}) cannot exceed maximum_words ({max_words})")

    wp = config.get("wordpress", {})
    if wp.get("status") not in ["draft", "publish"]:
        raise ValueError("wordpress.status must be 'draft' or 'publish'")

    pub = config.get("publishing", {})
    if pub.get("duplicate_policy") not in ["stop", "update_existing_draft", "create_new_version"]:
        raise ValueError("publishing.duplicate_policy must be one of: stop, update_existing_draft, create_new_version")

    logger.info("Job configuration validated successfully.")


def sanitize_html_content(raw_html: str) -> str:
    """Sanitizes HTML content ensuring safety for WordPress block editor insertion."""
    allowed_tags = [
        'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'strong', 'b', 'em', 'i',
        'ul', 'ol', 'li', 'a', 'img', 'figure', 'figcaption', 'table', 'thead', 'tbody',
        'tr', 'th', 'td', 'div', 'span', 'code', 'pre', 'hr', 'iframe'
    ]
    allowed_attributes = {
        'a': ['href', 'title', 'target', 'rel'],
        'img': ['src', 'alt', 'title', 'width', 'height', 'class'],
        'iframe': ['src', 'width', 'height', 'frameborder', 'allow', 'allowfullscreen', 'title'],
        'div': ['class', 'id'],
        'p': ['class'],
        'h2': ['class', 'id'],
        'h3': ['class', 'id'],
        'table': ['class'],
        'td': ['colspan', 'rowspan'],
        'th': ['colspan', 'rowspan']
    }

    # Clean using bleach if installed, otherwise BeautifulSoup fallback
    if HAS_BLEACH:
        cleaned = bleach.clean(
            raw_html,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )
    else:
        cleaned = raw_html

    # Validate iframe src to only allow trusted YouTube embeds
    soup = BeautifulSoup(cleaned, "html.parser")
    for iframe in soup.find_all("iframe"):
        src = iframe.get("src", "")
        if not (src.startswith("https://www.youtube.com/embed/") or src.startswith("https://www.youtube-nocookie.com/embed/")):
            logger.warning(f"Removing unapproved iframe source: {src}")
            iframe.decompose()

    return str(soup)


def generate_slug(text: str) -> str:
    """Generates a clean URL-safe slug from text."""
    slug = text.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')
