import os

def sanitize_placeholders():
    out_md = "outputs/z2QLALwNwQw/article/article.md"
    out_html = "outputs/z2QLALwNwQw/article/article.html"

    with open(out_md, "r", encoding="utf-8") as f:
        md = f.read()

    md = md.replace("[Your Name]", "Muti").replace("[Creator Name]", "Creator").replace("[Podcast Name]", "the Podcast").replace("[Guest Name]", "your guest").replace("[Specific Topic]", "the episode topic").replace("[City Name]", "your city").replace("[Owner Name]", "Business Owner").replace("[Plumbing/HVAC/Dental]", "services")

    with open(out_md, "w", encoding="utf-8") as f:
        f.write(md)

    with open(out_html, "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("[Your Name]", "Muti").replace("[Creator Name]", "Creator").replace("[Podcast Name]", "the Podcast").replace("[Guest Name]", "your guest").replace("[Specific Topic]", "the episode topic").replace("[City Name]", "your city").replace("[Owner Name]", "Business Owner").replace("[Plumbing/HVAC/Dental]", "services")

    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[OK] Placeholders sanitized in article.md and article.html")

if __name__ == "__main__":
    sanitize_placeholders()
