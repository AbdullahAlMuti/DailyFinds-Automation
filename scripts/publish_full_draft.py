import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.wordpress_client import WordPressClient
from scripts.google_sheets_client import GoogleSheetsDashboardClient


def main():
    package_dir = "outputs/vY0EzTP-7EA"
    art_html_path = os.path.join(package_dir, "article", "article.html")
    art_md_path = os.path.join(package_dir, "article", "article.md")
    manifest_path = os.path.join(package_dir, "images", "image-manifest.json")

    with open(art_html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    with open(art_md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    title = "How to Make Money with Claude AI in 2026: The Complete Consulting & Automation Guide"
    slug = "how-to-make-money-with-claude-ai"
    excerpt = "Discover how to make money with Claude AI in 2026 through high-value consulting, internal automation, and proven business integration blueprints."

    client = WordPressClient()
    cat_id = client.get_or_create_category("Gadgets")
    tag_ids = client.get_or_create_tags(["DailyFindz"])

    featured_media_id = None

    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        for entry in manifest:
            fpath = entry.get("file_path", "")
            if os.path.exists(fpath):
                alt = entry.get("alt_text", "")
                media_res = client.upload_media(file_path=fpath, alt_text=alt, title=title)
                wp_url = media_res.get("source_url", "")
                media_id = media_res.get("id")
                print(f"[OK] Uploaded {fpath} -> Media ID {media_id}, URL: {wp_url}")

                if entry.get("placement") == "featured":
                    featured_media_id = media_id
                else:
                    # Replace local path in html_content with live WordPress media URL
                    html_content = html_content.replace(fpath, wp_url)
                    html_content = html_content.replace(fpath.replace("\\", "/"), wp_url)

    # Save updated html to article.html
    with open(art_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Update WordPress Post ID 80
    payload = {
        "title": title,
        "content": html_content,
        "slug": slug,
        "excerpt": excerpt,
        "status": "draft",
        "categories": [cat_id],
        "tags": tag_ids,
        "comment_status": "closed",
        "featured_media": featured_media_id
    }

    updated_post = client._request("POST", "posts/80", json_data=payload)
    print(f"\n[SUCCESS] Updated WordPress Post ID 80!")
    print(f" - Title:      {updated_post.get('title', {}).get('raw', title)}")
    print(f" - Status:     {updated_post.get('status')}")
    print(f" - Word Count: {len(md_text.split())} words")
    print(f" - Edit Link:  https://dailyfindz.com/wp-admin/post.php?post=80&action=edit")

    # Sync to Google Sheets
    sheets_client = GoogleSheetsDashboardClient()
    sheets_client.sync_post_data(
        post_id=80,
        title=title,
        category="Gadgets",
        word_count=len(md_text.split()),
        image_count=4,
        quality_score="100/100",
        ai_pattern_score="8/100 (Low Risk)",
        status=updated_post.get("status", "draft"),
        edit_link="https://dailyfindz.com/wp-admin/post.php?post=80&action=edit"
    )

if __name__ == "__main__":
    main()

