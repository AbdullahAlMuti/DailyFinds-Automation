# Image Generation Rules & Prompt Engineering

All images must be generated using Antigravity's native `generate_image` tool.

## Technical Specifications
- **Featured Image**: 1 image, 16:9 aspect ratio, high resolution (compressed to ≤1200px width WEBP/JPEG, <150KB for upload).
- **Supporting/Inline Images**: **Minimum 4, maximum 9** supporting images per article (total **5–10** including featured). Each 16:9 aspect ratio. This meets the AdSense image-richness standard.
- **NO YouTube or video embeds**: Do NOT include any YouTube iframes, WordPress `wp:embed`, oEmbed blocks, or `<iframe>` tags inside the article. Replace all video content with generated images.
- **Filenames**: Hyphenated, descriptive, lower-case (`primary-keyword-featured.webp`, `topic-step-one.webp`).

## Prompt Guidelines
- **Style**: Editorial photography, clean realistic aesthetic, soft natural lighting.
- **Coverage**: Each inline image should visually represent a distinct section or concept of the article. Space them evenly across the body content — approximately every 2 H2 sections.
- **Negative Constraints**:
  - NO embedded text, typography, titles, or floating words.
  - NO brand logos, trademarks, or copyrighted symbols.
  - NO recognizable celebrity or public figure likenesses without authorization.
  - NO glossy AI art clichés or distorted hands/faces.
  - NO YouTube logos, video player UI, or play buttons.

## Manifest Requirement
Every generated image must be recorded in `outputs/<VIDEO_ID>/images/image-manifest.json` with:
- File path
- Intended placement (`featured`, `inline-1` through `inline-9`)
- Detailed generation prompt
- Alt text
- Caption
- Suggested filename
- AI-generated flag (`true`)
