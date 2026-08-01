import os
import unittest
from unittest.mock import patch, MagicMock

from scripts.google_sheets_client import GoogleSheetsDashboardClient


class TestGoogleSheetsDashboardClient(unittest.TestCase):

    def test_sync_skipped_when_no_webhook_url(self):
        client = GoogleSheetsDashboardClient(webhook_url="")
        result = client.sync_post_data(
            post_id=99,
            title="Test Post",
            category="Gadgets",
            word_count=3200,
            image_count=4,
            quality_score="100/100",
            ai_pattern_score="8/100 (Low Risk)",
            status="draft",
            edit_link="https://dailyfindz.com/wp-admin/post.php?post=99&action=edit"
        )
        self.assertFalse(result)

    @patch("requests.post")
    def test_sync_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        client = GoogleSheetsDashboardClient(webhook_url="https://script.google.com/macros/s/MOCK/exec")
        result = client.sync_post_data(
            post_id=95,
            title="The Only 25 Ways to Make Money in 2026",
            category="Gadgets",
            word_count=3068,
            image_count=4,
            quality_score="100/100",
            ai_pattern_score="8/100 (Low Risk)",
            status="draft",
            edit_link="https://dailyfindz.com/wp-admin/post.php?post=95&action=edit"
        )

        self.assertTrue(result)
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args[1]
        self.assertEqual(call_kwargs["json"]["post_id"], 95)
        self.assertEqual(call_kwargs["json"]["word_count"], 3068)
        self.assertEqual(call_kwargs["json"]["image_count"], 4)
        self.assertEqual(call_kwargs["json"]["quality_score"], "100/100")

    @patch("requests.post")
    def test_sync_failure_gracefully_handled(self, mock_post):
        mock_post.side_effect = Exception("Network timeout")

        client = GoogleSheetsDashboardClient(webhook_url="https://script.google.com/macros/s/MOCK/exec")
        result = client.sync_post_data(
            post_id=95,
            title="Test Post Failure Resilience",
            category="Gadgets",
            word_count=3000,
            image_count=4,
            quality_score="100/100",
            ai_pattern_score="8/100 (Low Risk)",
            status="draft",
            edit_link="https://dailyfindz.com/wp-admin/post.php?post=95&action=edit"
        )

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
