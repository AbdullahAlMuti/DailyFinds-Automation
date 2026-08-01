import os, re, requests
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

base = os.getenv("WP_BASE_URL", "https://dailyfindz.com").rstrip("/")
r = requests.get(base + "/", timeout=20, headers={"Cache-Control": "no-cache", "Pragma": "no-cache"})
html = r.text

checks = ["dfz-latest", "wp-block-latest-posts", "dfz-hero", "dfz-hero-cats", "dfz-cat-card", "dfz-trust"]
for c in checks:
    status = "OK" if c in html else "MISSING"
    print(f"[{status}] {c}")

# Find any rendered post links in the latest-posts block
links = re.findall(r'wp-block-latest-posts__post-title[^"]*"[^>]*>([^<]+)', html)
print("\nLatest post titles rendered:", links[:5])

# Show a small context around the block
idx = html.find("wp-block-latest-posts")
if idx > -1:
    print("\n--- wp-block-latest-posts context (first 800 chars) ---")
    print(html[idx:idx+800])
else:
    print("\nBlock NOT found in rendered HTML. Snippet around 'dfz-latest':")
    idx2 = html.find("dfz-latest")
    if idx2 > -1:
        print(html[idx2:idx2+600])
