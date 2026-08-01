---
name: post-image-studio
description: Generates, resizes, crops, optimizes, and packages blog and WordPress post images using Antigravity native image generation and Pillow. Exports multi-size WebP/JPEG variants, SEO alt text, captions, and image-manifest.json.
---

# Post Image Studio Skill for Antigravity 2.0

An end-to-end image production and optimization studio for blog articles and WordPress posts. All image generation uses Antigravity's native `generate_image` tool without external API keys.

---

## Production Workflow

1. **Prompt Creation**:
   - Formulate 16:9 editorial visual prompts based on the article title, topic, primary keyword, and summary.
   - Enforce clean, modern, realistic photography without heavy text overlays or brand logos.
2. **Native Image Generation**:
   - Generate 1 Featured Image (16:9).
   - Generate **minimum 4, up to 9** Supporting/Inline Images (16:9) — total **5–10** images per article (AdSense approval requirement).
   - **NEVER** embed YouTube iframes, oEmbed blocks, or video shortcodes. Use generated images only.
3. **Resizing & Cropping (`scripts/resize_images.py`)**:
   - Process images with Pillow (`PIL`) into defined size profiles (Featured, Inline, Social).
4. **Optimization (`scripts/optimize_images.py`)**:
   - Compress variants to WebP (quality 80) and progressive JPEG (quality 82, <150KB).
5. **Metadata & Manifest Export (`scripts/image_manifest.py`)**:
   - Generate SEO slug filenames, descriptive alt text, captions, and `image-manifest.json`.

---

## Output Size Profiles

### Featured Image
- `1600x900` webp (High-DPI Hero)
- `1200x630` jpg (Open Graph / Facebook)
- `768x432` webp (Mobile Header)

### Inline Supporting Images
- `1600x900` webp (Desktop Full-Width)
- `1200x675` webp (Standard Body Content)

### Social Media Variants
- `1200x630` jpg (LinkedIn / Twitter)
- `1080x1080` jpg (Instagram Square)
- `1080x1350` jpg (Instagram Portrait)

---

## Execution Command

```bash
# Resize & crop an original image
python scripts/resize_images.py --src outputs/<ID>/images/raw_featured.jpg --output-dir outputs/<ID>/images/ --name best-ai-side-hustles-featured --placement featured

# Optimize generated variants
python scripts/optimize_images.py --path outputs/<ID>/images/
```
