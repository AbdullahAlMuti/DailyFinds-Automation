"""
update_homepage.py
Adds a "Latest Posts" section to the DailyFindz homepage (page ID 49)
using the native WordPress core/latest-posts Gutenberg block with
GeneratePress-default post card styling.
"""

import os
import sys
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

base = os.getenv("WP_BASE_URL", "https://dailyfindz.com").rstrip("/")
auth = HTTPBasicAuth(os.getenv("WP_USERNAME", ""), os.getenv("WP_APP_PASSWORD", ""))

# ── NEW HOMEPAGE CONTENT ────────────────────────────────────────────────────
# Structure:
#   1. Hero banner  (custom HTML block)
#   2. Latest Finds (core/latest-posts block in 3-col grid with featured image)
#   3. Shop by Category  (custom HTML block)
#   4. Why Trust DailyFindz (inside category block)
# ────────────────────────────────────────────────────────────────────────────

CSS = """
.dfz-home{margin:0;}
body.home{overflow-x:hidden;}

/* ── Hero ── */
.dfz-hero{background:linear-gradient(135deg,#1e3a8a 0%,#1D4ED8 70%,#2563eb 100%);padding:60px 24px;width:100vw;position:relative;left:50%;margin-left:-50vw;}
.dfz-hero-in{max-width:1180px;margin:0 auto;}
.dfz-hero-title{color:#fff;font-size:clamp(30px,4.4vw,44px);font-weight:800;letter-spacing:-.02em;line-height:1.12;margin:0 0 14px;}
.dfz-hero-sub{color:#dbeafe;font-size:clamp(15px,1.7vw,18px);max-width:64ch;margin:0 0 26px;line-height:1.65;}
.dfz-hero-cats{display:flex;flex-wrap:wrap;gap:12px;}
.dfz-hero-cats a{display:inline-block;padding:10px 20px;border:1px solid rgba(255,255,255,.4);border-radius:999px;color:#fff;font-weight:600;font-size:14.5px;text-decoration:none;background:rgba(255,255,255,.10);transition:all .15s ease;}
.dfz-hero-cats a:hover{background:#F59E0B;border-color:#F59E0B;color:#0f172a;}

/* ── Shared section wrapper ── */
.dfz-sec{max-width:1180px;margin:0 auto;padding:52px 24px 8px;}
.dfz-sec-title{font-size:clamp(22px,2.6vw,30px);font-weight:800;color:#0f172a;letter-spacing:-.01em;margin:0 0 6px;}
.dfz-sec-sub{color:#64748b;margin:0 0 28px;font-size:16px;}

/* ── Category cards ── */
.dfz-cats{display:grid;grid-template-columns:repeat(4,1fr);gap:22px;}
.dfz-cat-card{background:#fff;border:1px solid #e2e8f0;border-top:4px solid #1D4ED8;border-radius:12px;padding:26px 24px;text-decoration:none;display:block;transition:transform .15s ease,box-shadow .15s ease;}
.dfz-cat-card:hover{transform:translateY(-3px);box-shadow:0 12px 28px rgba(15,23,42,.10);}
.dfz-cat-card h3{color:#0f172a;font-size:18px;font-weight:800;margin:0 0 8px;}
.dfz-cat-card p{color:#475569;font-size:14.5px;line-height:1.6;margin:0 0 12px;}
.dfz-cat-card span{color:#1D4ED8;font-weight:700;font-size:14px;}
.dfz-cat-card:hover span{color:#F59E0B;}

/* ── Latest Finds section header ── */
.dfz-latest{max-width:1180px;margin:0 auto;padding:52px 24px 32px;}
.dfz-latest-header{display:flex;align-items:baseline;justify-content:space-between;margin-bottom:28px;flex-wrap:wrap;gap:12px;}
.dfz-latest-header h2{font-size:clamp(22px,2.6vw,30px);font-weight:800;color:#0f172a;letter-spacing:-.01em;margin:0;}
.dfz-latest-header a{color:#1D4ED8;font-weight:600;font-size:15px;text-decoration:none;}
.dfz-latest-header a:hover{color:#F59E0B;}

/* ── Override core/latest-posts to match site style ── */
.dfz-latest-grid.wp-block-latest-posts{
  list-style:none;margin:0;padding:0;
  display:grid;grid-template-columns:repeat(3,1fr);gap:24px;
}
.dfz-latest-grid.wp-block-latest-posts li{
  background:#fff;border:1px solid #e2e8f0;border-radius:12px;
  overflow:hidden;display:flex;flex-direction:column;
  transition:transform .15s ease,box-shadow .15s ease;
}
.dfz-latest-grid.wp-block-latest-posts li:hover{
  transform:translateY(-3px);box-shadow:0 12px 28px rgba(15,23,42,.10);
}
/* Thumbnail */
.dfz-latest-grid .wp-block-latest-posts__featured-image{
  aspect-ratio:16/9;overflow:hidden;background:#f1f5f9;
  flex-shrink:0;
}
.dfz-latest-grid .wp-block-latest-posts__featured-image img{
  width:100%;height:100%;object-fit:cover;display:block;
  transition:transform .3s ease;
}
.dfz-latest-grid li:hover .wp-block-latest-posts__featured-image img{
  transform:scale(1.05);
}
/* Post text area */
.dfz-latest-grid .wp-block-latest-posts__post-title{
  display:block;font-size:17px;font-weight:700;color:#0f172a;
  text-decoration:none;line-height:1.4;padding:16px 18px 6px;
}
.dfz-latest-grid .wp-block-latest-posts__post-title:hover{color:#1D4ED8;}
.dfz-latest-grid time{
  font-size:12.5px;color:#94a3b8;display:block;
  padding:0 18px 8px;
}
.dfz-latest-grid .wp-block-latest-posts__post-excerpt{
  font-size:14px;color:#475569;line-height:1.65;
  padding:0 18px 18px;flex:1;
}

/* ── Trust box ── */
.dfz-trust{background:#fff;border:1px solid #e2e8f0;border-radius:14px;padding:38px 34px;margin:48px auto 56px;max-width:1132px;}
.dfz-trust-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:30px;margin-top:22px;}
.dfz-trust-item h3{font-size:16px;font-weight:800;color:#0f172a;margin:0 0 8px;padding-left:14px;border-left:4px solid #F59E0B;}
.dfz-trust-item p{color:#475569;font-size:14.5px;line-height:1.65;margin:0;}
.dfz-trust-links{margin-top:24px;font-size:14.5px;color:#64748b;}

/* ── Responsive ── */
@media(max-width:980px){
  .dfz-cats{grid-template-columns:repeat(2,1fr);}
  .dfz-trust-grid{grid-template-columns:1fr;gap:20px;}
  .dfz-latest-grid.wp-block-latest-posts{grid-template-columns:repeat(2,1fr);}
}
@media(max-width:560px){
  .dfz-cats{grid-template-columns:1fr;}
  .dfz-hero{padding:44px 20px;}
  .dfz-latest-grid.wp-block-latest-posts{grid-template-columns:1fr;}
  .dfz-latest{padding:36px 16px 24px;}
}
""".strip()

HERO_HTML = """
<div class="dfz-home">
  <div class="dfz-hero">
    <div class="dfz-hero-in">
      <div class="dfz-hero-title">Smart Deals. Honest Finds. Every&nbsp;Day.</div>
      <p class="dfz-hero-sub">DailyFindz hunts down the best discounts and genuinely useful products across Home &amp; Kitchen, Electronics, Beauty, and Gadgets &mdash; researched, compared, and honestly reviewed before we recommend anything.</p>
      <div class="dfz-hero-cats">
        <a href="https://dailyfindz.com/category/home-kitchen/">Home &amp; Kitchen</a>
        <a href="https://dailyfindz.com/category/electronics/">Electronics</a>
        <a href="https://dailyfindz.com/category/beauty/">Beauty</a>
        <a href="https://dailyfindz.com/category/gadgets/">Gadgets</a>
        <a href="https://dailyfindz.com/category/business-ai/">Business &amp; AI</a>
      </div>
    </div>
  </div>
</div>
""".strip()

LATEST_HEADER_HTML = """
<div class="dfz-latest">
  <div class="dfz-latest-header">
    <h2>Latest Finds</h2>
    <a href="https://dailyfindz.com/finds/">View all posts &rarr;</a>
  </div>
""".strip()

LATEST_FOOTER_HTML = "</div>"  # close .dfz-latest

CATS_HTML = """
<div class="dfz-sec">
  <h2 class="dfz-sec-title">Shop by Category</h2>
  <p class="dfz-sec-sub">Every category is curated the same way: real research, price comparisons, and picks we&rsquo;d recommend to a friend.</p>
  <div class="dfz-cats">
    <a class="dfz-cat-card" href="https://dailyfindz.com/category/home-kitchen/">
      <h3>Home &amp; Kitchen</h3>
      <p>Cookware, appliances, and home essentials that earn their counter space &mdash; at the best prices we can find.</p>
      <span>Browse deals &rarr;</span>
    </a>
    <a class="dfz-cat-card" href="https://dailyfindz.com/category/electronics/">
      <h3>Electronics</h3>
      <p>Audio, screens, chargers, and accessories &mdash; specs checked, reviews read, duds filtered out.</p>
      <span>Browse deals &rarr;</span>
    </a>
    <a class="dfz-cat-card" href="https://dailyfindz.com/category/beauty/">
      <h3>Beauty</h3>
      <p>Skincare, grooming, and beauty tools that actually deliver &mdash; no miracle claims, just honest picks.</p>
      <span>Browse deals &rarr;</span>
    </a>
    <a class="dfz-cat-card" href="https://dailyfindz.com/category/gadgets/">
      <h3>Gadgets</h3>
      <p>Smart devices and clever gadgets worth your money &mdash; tested against the hype before we feature them.</p>
      <span>Browse deals &rarr;</span>
    </a>
  </div>

  <div class="dfz-trust">
    <h2 class="dfz-sec-title">Why trust DailyFindz?</h2>
    <div class="dfz-trust-grid">
      <div class="dfz-trust-item">
        <h3>Genuine research</h3>
        <p>We check specifications, compare alternatives, and read verified customer feedback before featuring any product.</p>
      </div>
      <div class="dfz-trust-item">
        <h3>Value first</h3>
        <p>A deal only makes the cut when the product itself is worth owning. A discount on a bad product is still a bad buy.</p>
      </div>
      <div class="dfz-trust-item">
        <h3>Honest recommendations</h3>
        <p>If we wouldn&rsquo;t buy it ourselves or suggest it to a friend, it doesn&rsquo;t get published. Simple as that.</p>
      </div>
    </div>
    <p class="dfz-trust-links">Read how we work in our <a href="https://dailyfindz.com/editorial-policy/">Editorial Policy</a>, or learn more <a href="https://dailyfindz.com/about/">about us</a>.</p>
  </div>
</div>
""".strip()

# ── Assemble Gutenberg block markup ─────────────────────────────────────────
# Block 1: shared CSS + hero HTML
block_hero = f"<!-- wp:html -->\n<style>\n{CSS}\n</style>\n{HERO_HTML}\n<!-- /wp:html -->"

# Block 2: "Latest Finds" section wrapper open
block_latest_open = f"<!-- wp:html -->\n{LATEST_HEADER_HTML}\n<!-- /wp:html -->"

# Block 3: core/latest-posts (native WP block — rendered server-side by GeneratePress)
# className targets our CSS grid overrides
block_latest_posts = (
    '<!-- wp:latest-posts '
    '{"postsToShow":6,'
    '"displayPostContent":true,'
    '"displayPostContentRadio":"excerpt",'
    '"excerptLength":20,'
    '"displayPostDate":true,'
    '"displayFeaturedImage":true,'
    '"featuredImageAlign":"center",'
    '"featuredImageSizeSlug":"medium_large",'
    '"addLinkToFeaturedImage":true,'
    '"postLayout":"grid",'
    '"columns":3,'
    '"className":"dfz-latest-grid"} /-->'
)

# Block 4: close .dfz-latest div
block_latest_close = f"<!-- wp:html -->\n{LATEST_FOOTER_HTML}\n<!-- /wp:html -->"

# Block 5: Category cards + trust section
block_cats = f"<!-- wp:html -->\n{CATS_HTML}\n<!-- /wp:html -->"

new_content = "\n\n".join([
    block_hero,
    block_latest_open,
    block_latest_posts,
    block_latest_close,
    block_cats,
])

# ── Push to WordPress ────────────────────────────────────────────────────────
print("Updating homepage (page ID 49)...")
r = requests.post(
    f"{base}/wp-json/wp/v2/pages/49",
    auth=auth,
    timeout=30,
    json={"content": new_content, "status": "publish"},
)
print(f"HTTP {r.status_code}")
data = r.json()
if r.status_code in [200, 201]:
    print(f"[OK] Page updated successfully")
    print(f"     Link:     {data.get('link', '')}")
    print(f"     Modified: {data.get('modified', '')}")
else:
    print(f"[ERROR] {r.text[:600]}")
    sys.exit(1)
