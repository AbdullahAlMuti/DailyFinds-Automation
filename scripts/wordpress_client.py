"""
WordPress REST API Client for DailyFindz.
Handles authentication, category/tag lookup & creation, media upload with metadata,
post creation/updating, duplicate protection, read-back verification, and publication locks.
"""

import os
import json
import re
import sys
from typing import Dict, Any, List, Optional, Tuple
import requests
from requests.auth import HTTPBasicAuth

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.utilities import logger


class WordPressAPIError(Exception):
    """Custom exception for WordPress REST API errors."""
    pass


class WordPressClient:
    """Client for WordPress REST API operations."""

    CATEGORY_MAPPING = {
        "business & ai": 25,
        "business-ai": 25,
        "business": 25,
        "ai": 25,
        "home & kitchen": 3,
        "home-kitchen": 3,
        "electronics": 4,
        "beauty": 5,
        "gadgets": 6,
    }

    @classmethod
    def determine_best_category(cls, title: str, content: str = "") -> str:
        """Dynamically determines the best matching fixed category based on title and content keywords."""
        combined_text = (title + " " + content).lower()
        
        business_keywords = ["make money", "claude", "side hustle", "ai consulting", "automation", "wealth", "business", "freelance", "income", "earn", "saas", "agency"]
        beauty_keywords = ["skincare", "beauty", "cosmetics", "haircare", "makeup", "facial"]
        home_keywords = ["kitchen", "home", "organizer", "cookware", "decor", "cleaning", "furniture"]
        electronics_keywords = ["laptop", "monitor", "software", "headphone", "audio", "hardware", "camera"]
        
        if any(kw in combined_text for kw in business_keywords):
            return "Business & AI"
        elif any(kw in combined_text for kw in beauty_keywords):
            return "Beauty"
        elif any(kw in combined_text for kw in home_keywords):
            return "Home & Kitchen"
        elif any(kw in combined_text for kw in electronics_keywords):
            return "Electronics"
        else:
            return "Gadgets"


    def __init__(
        self,
        base_url: Optional[str] = None,
        username: Optional[str] = None,
        app_password: Optional[str] = None,
        timeout: int = 30,
        verify_ssl: bool = True
    ):
        self.base_url = (base_url or os.getenv("WP_BASE_URL", "https://dailyfindz.com")).rstrip("/")
        self.username = username or os.getenv("WP_USERNAME", "")
        self.app_password = app_password or os.getenv("WP_APP_PASSWORD", "")
        self.timeout = int(os.getenv("WP_REQUEST_TIMEOUT", str(timeout)))
        self.verify_ssl = os.getenv("WP_VERIFY_SSL", "true").lower() == "true" if verify_ssl else False

        self.auth = HTTPBasicAuth(self.username, self.app_password) if self.username and self.app_password else None

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Any:
        """Helper to send HTTP requests to WordPress REST API with error handling."""
        url = f"{self.base_url}/wp-json/wp/v2/{endpoint.lstrip('/')}"
        req_headers = headers or {}

        try:
            response = requests.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                files=files,
                headers=req_headers,
                auth=self.auth,
                timeout=self.timeout,
                verify=self.verify_ssl
            )

            if response.status_code in [200, 201]:
                return response.json()

            # Exception handling for error codes
            status_code = response.status_code
            error_msg = f"WordPress REST API error {status_code} on {method} {url}"

            try:
                err_data = response.json()
                if isinstance(err_data, dict):
                    error_msg += f": {err_data.get('message', '')} ({err_data.get('code', '')})"
            except Exception:
                error_msg += f": {response.text[:200]}"

            if status_code == 401:
                raise WordPressAPIError(f"Authentication failure (401). Verify WP_USERNAME and WP_APP_PASSWORD. Detail: {error_msg}")
            elif status_code == 403:
                raise WordPressAPIError(f"Permission denied (403). User lacks rights. Detail: {error_msg}")
            elif status_code == 404:
                raise WordPressAPIError(f"Endpoint or resource not found (404). Detail: {error_msg}")
            elif status_code == 413:
                raise WordPressAPIError(f"Media file upload size too large (413). Detail: {error_msg}")
            elif status_code == 429:
                raise WordPressAPIError(f"Rate limited by WordPress host (429). Detail: {error_msg}")
            else:
                raise WordPressAPIError(error_msg)

        except requests.Timeout:
            raise WordPressAPIError(f"Request timeout after {self.timeout}s to {url}")
        except requests.RequestException as e:
            raise WordPressAPIError(f"Network request exception connecting to WordPress: {e}")

    def test_authentication(self) -> Dict[str, Any]:
        """Tests WordPress API connection and returns current user details."""
        logger.info("Testing WordPress REST API authentication...")
        user_info = self._request("GET", "users/me")
        logger.info(f"Successfully authenticated as WordPress User: '{user_info.get('name')}' (ID: {user_info.get('id')})")
        return user_info

    def get_or_create_category(self, category_name: str) -> int:
        """Looks up a category by name/slug or creates it. Returns term ID."""
        cat_lower = category_name.lower().strip()
        if cat_lower in self.CATEGORY_MAPPING:
            return self.CATEGORY_MAPPING[cat_lower]

        # Search category via API
        results = self._request("GET", "categories", params={"search": category_name})
        if results and isinstance(results, list):
            for cat in results:
                if cat.get("name", "").lower() == cat_lower or cat.get("slug", "").lower() == cat_lower:
                    return cat["id"]

        # Create category if not found
        logger.info(f"Category '{category_name}' not found. Creating category...")
        new_cat = self._request("POST", "categories", json_data={"name": category_name})
        return new_cat["id"]

    def get_or_create_tags(self, tag_names: List[str]) -> List[int]:
        """Resolves list of tag names to term IDs, creating missing tags."""
        tag_ids = []
        for tag in tag_names:
            tag = tag.strip()
            if not tag:
                continue
            results = self._request("GET", "tags", params={"search": tag})
            found_id = None
            if results and isinstance(results, list):
                for t in results:
                    if t.get("name", "").lower() == tag.lower():
                        found_id = t["id"]
                        break

            if not found_id:
                logger.info(f"Tag '{tag}' not found. Creating tag...")
                new_t = self._request("POST", "tags", json_data={"name": tag})
                found_id = new_t["id"]

            tag_ids.append(found_id)
        return tag_ids

    def search_duplicate_post(self, slug: str, title: str) -> Optional[Dict[str, Any]]:
        """Searches existing WordPress posts by exact slug or normalized title."""
        # 1. Search by slug
        try:
            posts = self._request("GET", "posts", params={"slug": slug, "status": "any"})
        except WordPressAPIError:
            posts = self._request("GET", "posts", params={"slug": slug})

        if posts and isinstance(posts, list) and len(posts) > 0:
            return posts[0]

        # 2. Search by title
        try:
            posts_title = self._request("GET", "posts", params={"search": title, "status": "any"})
        except WordPressAPIError:
            posts_title = self._request("GET", "posts", params={"search": title})

        if posts_title and isinstance(posts_title, list):
            for p in posts_title:
                if p.get("title", {}).get("rendered", "").strip().lower() == title.strip().lower():
                    return p

        return None

    def upload_media(
        self,
        file_path: str,
        alt_text: str = "",
        title: str = "",
        caption: str = "",
        description: str = ""
    ) -> Dict[str, Any]:
        """Uploads an image file to WordPress Media Library and sets metadata."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Media file not found for upload: {file_path}")

        filename = os.path.basename(file_path)
        logger.info(f"Uploading media '{filename}' to WordPress...")

        with open(file_path, "rb") as f:
            file_bytes = f.read()

        # Determine mime type
        ext = filename.split(".")[-1].lower()
        content_type = "image/webp" if ext == "webp" else "image/jpeg"

        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": content_type
        }

        url = f"{self.base_url}/wp-json/wp/v2/media"
        response = requests.post(
            url,
            data=file_bytes,
            headers=headers,
            auth=self.auth,
            timeout=self.timeout,
            verify=self.verify_ssl
        )

        if response.status_code not in [200, 201]:
            raise WordPressAPIError(f"Media upload failed ({response.status_code}): {response.text[:200]}")

        media_data = response.json()
        media_id = media_data["id"]

        # Update media metadata (alt_text, title, caption, description)
        meta_payload = {}
        if alt_text:
            meta_payload["alt_text"] = alt_text
        if title:
            meta_payload["title"] = title
        if caption:
            meta_payload["caption"] = caption
        if description:
            meta_payload["description"] = description

        if meta_payload:
            self._request("POST", f"media/{media_id}", json_data=meta_payload)

        logger.info(f"Media '{filename}' uploaded successfully (Media ID: {media_id})")
        return media_data

    # ------------------------------------------------------------------
    # YouTube / video embed stripping
    # ------------------------------------------------------------------

    _YOUTUBE_EMBED_PATTERNS = [
        re.compile(r'<!-- wp:embed.*?<!-- /wp:embed -->', re.DOTALL),
        re.compile(r'<iframe[^>]*(?:youtube|youtu\.be|vimeo|video)[^>]*>.*?</iframe>', re.DOTALL | re.IGNORECASE),
        re.compile(r'<iframe[^>]*>.*?</iframe>', re.DOTALL | re.IGNORECASE),
        re.compile(r'\[embed\].*?\[/embed\]', re.DOTALL | re.IGNORECASE),
        re.compile(r'(?m)^https?://(?:www\.)?(?:youtube\.com|youtu\.be)/\S+\s*$'),
    ]

    def _strip_video_embeds(self, html: str) -> str:
        """Remove YouTube iframes, oEmbed blocks, and bare video URLs from HTML."""
        for pattern in self._YOUTUBE_EMBED_PATTERNS:
            html = pattern.sub('', html)
        html = re.sub(r'\n{3,}', '\n\n', html)
        return html

    def create_post(
        self,
        title: str,
        content_html: str,
        slug: str,
        excerpt: str,
        category_id: int,
        tag_ids: List[int],
        featured_media_id: Optional[int] = None,
        author_id: Optional[int] = None,
        requested_status: str = "draft",
        allow_publish_flag: bool = False
    ) -> Dict[str, Any]:
        """
        Creates or updates a WordPress post enforcing safety tri-locks.
        Automatically strips YouTube embeds and iframes before upload.
        """
        # Strip any YouTube / video embeds before posting
        content_html = self._strip_video_embeds(content_html)
        # Determine status via tri-lock
        env_allow_pub = os.getenv("WP_ALLOW_PUBLICATION", "false").lower() == "true"
        final_status = "draft"
        if requested_status == "publish" and env_allow_pub and allow_publish_flag:
            final_status = "publish"
        else:
            if requested_status == "publish":
                logger.warning("Publication requested but blocked by safety locks (env or CLI flag missing). Forcing status to 'draft'.")

        payload = {
            "title": title,
            "content": content_html,
            "slug": slug,
            "excerpt": excerpt,
            "status": final_status,
            "categories": [category_id],
            "tags": tag_ids,
            "comment_status": "closed",
        }
        if author_id:
            payload["author"] = author_id

        if featured_media_id:
            payload["featured_media"] = featured_media_id

        logger.info(f"Creating WordPress post '{title}' (Status: {final_status})...")
        post = self._request("POST", "posts", json_data=payload)
        post_id = post["id"]
        logger.info(f"Post created successfully (Post ID: {post_id})")

        # Read-back verification
        verified_post = self.verify_post_readback(post_id)
        return verified_post

    def verify_post_readback(self, post_id: int) -> Dict[str, Any]:
        """Reads back post from WordPress to verify creation integrity."""
        logger.info(f"Performing read-back verification for Post ID {post_id}...")
        post = self._request("GET", f"posts/{post_id}")
        rendered_content = post.get("content", {}).get("rendered", "")
        if not rendered_content.strip():
            raise WordPressAPIError(f"Read-back verification failed: Post ID {post_id} content is empty after creation.")

        logger.info(f"Read-back verification PASSED for Post ID {post_id}.")
        return post
