import os
import json
from PIL import Image, ImageDraw, ImageFont

def create_educational_diagram(filename, title_text, subtitle_text, color_theme="blue"):
    width, height = 1600, 900
    if color_theme == "blue":
        bg_color = (15, 23, 42)
        card_color = (30, 41, 59)
        text_color = (255, 255, 255)
        accent_color = (56, 189, 248)
    elif color_theme == "green":
        bg_color = (6, 78, 59)
        card_color = (4, 120, 87)
        text_color = (255, 255, 255)
        accent_color = (52, 211, 153)
    else:
        bg_color = (30, 27, 75)
        card_color = (67, 56, 202)
        text_color = (255, 255, 255)
        accent_color = (165, 180, 252)

    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Draw background grid card
    draw.rectangle([80, 80, width - 80, height - 80], fill=card_color, outline=accent_color, width=4)

    # Try loading default fonts
    try:
        title_font = ImageFont.truetype("arial.ttf", 54)
        subtitle_font = ImageFont.truetype("arial.ttf", 32)
        watermark_font = ImageFont.truetype("arial.ttf", 24)
    except IOError:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        watermark_font = ImageFont.load_default()

    # Draw Watermark / Header Pill
    draw.rectangle([120, 120, 420, 180], fill=accent_color)
    draw.text((140, 135), "DAILYFINDZ EDITORIAL", fill=(15, 23, 42), font=watermark_font)

    # Draw Title
    draw.text((120, 260), title_text, fill=text_color, font=title_font)
    
    # Draw Subtitle
    draw.text((120, 360), subtitle_text, fill=accent_color, font=subtitle_font)

    # Draw 3 Workflow Steps Cards
    steps = [
        ("Step 1: Skill Audit", "Identify high-value digital services"),
        ("Step 2: Client Offer", "Package outcome-based retainers"),
        ("Step 3: Execution", "Deliver verified business returns")
    ]
    
    card_w = 420
    for i, (s_title, s_desc) in enumerate(steps):
        x = 120 + i * (card_w + 30)
        y = 480
        draw.rectangle([x, y, x + card_w, y + 260], fill=bg_color, outline=accent_color, width=2)
        draw.text((x + 20, y + 30), s_title, fill=accent_color, font=subtitle_font)
        draw.text((x + 20, y + 100), s_desc, fill=text_color, font=watermark_font)

    img.save(filename, "JPEG", quality=95)
    print(f"[OK] Generated visual graphic: {filename}")

def main():
    target_dir = "outputs/z2QLALwNwQw/images"
    os.makedirs(target_dir, exist_ok=True)

    create_educational_diagram(
        os.path.join(target_dir, "inline1.jpg"),
        "Halal Earning Framework 2026",
        "Evaluating Ethical Digital Business Models & Revenue Streams",
        color_theme="blue"
    )

    create_educational_diagram(
        os.path.join(target_dir, "inline2.jpg"),
        "The $100/Day Digital Roadmap",
        "Skill Acquisition, Client Pitching & Retainer Scaling",
        color_theme="green"
    )

    create_educational_diagram(
        os.path.join(target_dir, "inline3.jpg"),
        "Risk Mitigation & E-E-A-T Quality",
        "Avoiding Speculative Hustles & Building Sustainable Assets",
        color_theme="purple"
    )

    # Copy native hero image if present or create featured.jpg
    hero_src = r"C:\Users\MUTI\.gemini\antigravity\brain\fecc3366-8ae6-460b-a38a-b89f15b42950\halal_money_2026_feat_1785607580778.jpg"
    feat_dst = os.path.join(target_dir, "featured.jpg")
    if os.path.exists(hero_src):
        img_h = Image.open(hero_src)
        img_h.convert("RGB").save(feat_dst, "JPEG", quality=95)
        print(f"[OK] Copied native hero image to: {feat_dst}")
    else:
        create_educational_diagram(feat_dst, "7 Halal Ways to Make $100/Day in 2026", "Master Guide by DailyFindz Editorial", color_theme="blue")

if __name__ == "__main__":
    main()
