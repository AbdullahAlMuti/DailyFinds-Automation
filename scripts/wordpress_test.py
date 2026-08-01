"""
WordPress REST API Connection Tester CLI.
Tests credentials and site connectivity without modifying site content.
"""

import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.wordpress_client import WordPressClient, WordPressAPIError
from scripts.utilities import logger, setup_logger

setup_logger()


def test_connection() -> bool:
    """Executes WordPress connection test."""
    print("=" * 60)
    print("      WordPress REST API Connection Diagnostic Test")
    print("=" * 60)

    base_url = os.getenv("WP_BASE_URL", "https://dailyfindz.com")
    username = os.getenv("WP_USERNAME", "")
    print(f"Target Site URL: {base_url}")
    print(f"WordPress User : {username}")
    print(f"App Password   : [REDACTED]")

    client = WordPressClient()

    try:
        user_info = client.test_authentication()
        print("\n[OK] Authentication Successful!")
        print(f"   - User ID          : {user_info.get('id')}")
        print(f"   - Display Name     : {user_info.get('name')}")
        print(f"   - Username         : {user_info.get('slug')}")
        print(f"   - Capabilities     : {list(user_info.get('capabilities', {}).keys())[:5]}")

        # Check default categories
        cat_id = client.get_or_create_category("Home & Kitchen")
        print(f"   - Default Category 'Home & Kitchen' ID: {cat_id}")

        print("\nWordPress REST API is fully operational and authenticated.")
        return True

    except WordPressAPIError as e:
        print(f"\n[FAIL] Connection Failed: {e}")
        return False
    except Exception as e:
        print(f"\n[FAIL] Unexpected Error: {e}")
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
