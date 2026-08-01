"""
Google Sheets Dashboard Client for DailyFindz.
Syncs WordPress post metrics and quality scores to a real-time Google Sheets dashboard.
Supports Google Apps Script Webhooks (recommended) and Service Account API.
"""

import os
import json
import datetime
from typing import Dict, Any, Optional
import requests

from scripts.utilities import logger


class GoogleSheetsSyncError(Exception):
    """Custom exception for Google Sheets sync errors."""
    pass


class GoogleSheetsDashboardClient:
    """Client for syncing post publishing metadata to Google Sheets Dashboard."""

    def __init__(self, webhook_url: Optional[str] = None, timeout: int = 15):
        if webhook_url is not None:
            self.webhook_url = webhook_url.strip()
        else:
            self.webhook_url = os.getenv("GOOGLE_SHEETS_WEBHOOK_URL", "").strip()
        self.timeout = timeout


    def sync_post_data(
        self,
        post_id: int,
        title: str,
        category: str,
        word_count: int,
        image_count: int,
        quality_score: str,
        ai_pattern_score: str,
        status: str,
        edit_link: str,
        timestamp: Optional[str] = None
    ) -> bool:
        """
        Sends post metadata payload to Google Sheets Webhook.
        Returns True if successful, False if skipped/failed without crashing.
        """
        if not self.webhook_url:
            logger.info("GOOGLE_SHEETS_WEBHOOK_URL is not set. Dashboard sync skipped.")
            return False

        if not timestamp:
            timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        payload = {
            "post_id": post_id,
            "title": title,
            "category": category,
            "word_count": word_count,
            "image_count": image_count,
            "quality_score": quality_score,
            "ai_pattern_score": ai_pattern_score,
            "status": status,
            "timestamp": timestamp,
            "edit_link": edit_link
        }

        logger.info(f"Syncing Post ID {post_id} metadata to Google Sheets Dashboard...")

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )

            if response.status_code in [200, 201, 302]:
                logger.info(f"Google Sheets Dashboard sync SUCCESSFUL for Post ID {post_id}.")
                return True
            else:
                logger.warning(f"Google Sheets Dashboard sync returned status code {response.status_code}: {response.text[:200]}")
                return False

        except Exception as e:
            logger.warning(f"Google Sheets Dashboard sync encountered an error (WordPress post creation unaffected): {str(e)}")
            return False
