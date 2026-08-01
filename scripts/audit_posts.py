import os, requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

base = os.getenv("WP_BASE_URL", "https://dailyfindz.com").rstrip("/")
auth = HTTPBasicAuth(os.getenv("WP_USERNAME", ""), os.getenv("WP_APP_PASSWORD", ""))

for status in ["publish", "draft"]:
    r = requests.get(base + "/wp-json/wp/v2/posts", auth=auth, timeout=15,
        params={"status": status, "per_page": 100, "_fields": "id,title,status,link,featured_media"})
    posts = r.json()
    print(f"\nStatus={status}: {len(posts)} posts")
    for p in posts:
        pid = p["id"]
        title = p["title"]["rendered"][:65]
        fm = p.get("featured_media", 0)
        link = p.get("link", "")[-50:]
        print(f"  ID={pid} fm={fm} {title}")
        print(f"       {link}")
