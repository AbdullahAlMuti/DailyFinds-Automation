"""
Tests for WordPress Client module (authentication, post creation, duplicate check, publication safety lock).
Uses responses library to mock HTTP REST API calls.
"""

import os
import pytest
import responses
from scripts.wordpress_client import WordPressClient, WordPressAPIError


@responses.activate
def test_test_authentication_success():
    client = WordPressClient(base_url="https://dailyfindz.com", username="testuser", app_password="password123")
    responses.add(
        responses.GET,
        "https://dailyfindz.com/wp-json/wp/v2/users/me",
        json={"id": 1, "name": "Muti", "slug": "muti", "capabilities": {"administrator": True}},
        status=200
    )

    user_info = client.test_authentication()
    assert user_info["id"] == 1
    assert user_info["name"] == "Muti"


@responses.activate
def test_test_authentication_failure_401():
    client = WordPressClient(base_url="https://dailyfindz.com", username="baduser", app_password="wrongpassword")
    responses.add(
        responses.GET,
        "https://dailyfindz.com/wp-json/wp/v2/users/me",
        json={"code": "invalid_username", "message": "Invalid username"},
        status=401
    )

    with pytest.raises(WordPressAPIError) as exc_info:
        client.test_authentication()
    assert "Authentication failure (401)" in str(exc_info.value)


@responses.activate
def test_get_or_create_category_existing():
    client = WordPressClient(base_url="https://dailyfindz.com")
    # Home & Kitchen is in default mapping -> 3
    cat_id = client.get_or_create_category("Home & Kitchen")
    assert cat_id == 3


@responses.activate
def test_get_or_create_category_new():
    client = WordPressClient(base_url="https://dailyfindz.com")
    responses.add(
        responses.GET,
        "https://dailyfindz.com/wp-json/wp/v2/categories?search=CustomCategory",
        json=[],
        status=200
    )
    responses.add(
        responses.POST,
        "https://dailyfindz.com/wp-json/wp/v2/categories",
        json={"id": 99, "name": "CustomCategory"},
        status=201
    )

    cat_id = client.get_or_create_category("CustomCategory")
    assert cat_id == 99


@responses.activate
def test_create_post_enforces_draft_status_by_default(monkeypatch):
    monkeypatch.setenv("WP_ALLOW_PUBLICATION", "false")
    client = WordPressClient(base_url="https://dailyfindz.com")

    responses.add(
        responses.POST,
        "https://dailyfindz.com/wp-json/wp/v2/posts",
        json={"id": 101, "status": "draft"},
        status=201
    )

    responses.add(
        responses.GET,
        "https://dailyfindz.com/wp-json/wp/v2/posts/101",
        json={"id": 101, "status": "draft", "content": {"rendered": "<p>Content</p>"}},
        status=200
    )

    # Request status='publish' but lock forces 'draft'
    post = client.create_post(
        title="Test Post",
        content_html="<p>Content</p>",
        slug="test-post",
        excerpt="Test Excerpt",
        category_id=3,
        tag_ids=[],
        requested_status="publish",
        allow_publish_flag=False
    )

    assert post["id"] == 101
    assert post["status"] == "draft"


@responses.activate
def test_create_post_readback_verification_failure():
    client = WordPressClient(base_url="https://dailyfindz.com")

    responses.add(
        responses.POST,
        "https://dailyfindz.com/wp-json/wp/v2/posts",
        json={"id": 102, "status": "draft"},
        status=201
    )

    # Empty content on readback raises WordPressAPIError
    responses.add(
        responses.GET,
        "https://dailyfindz.com/wp-json/wp/v2/posts/102",
        json={"id": 102, "status": "draft", "content": {"rendered": ""}},
        status=200
    )

    with pytest.raises(WordPressAPIError) as exc_info:
        client.create_post(
            title="Empty Readback",
            content_html="<p>Content</p>",
            slug="empty-readback",
            excerpt="Excerpt",
            category_id=3,
            tag_ids=[],
            requested_status="draft"
        )
    assert "Read-back verification failed" in str(exc_info.value)
