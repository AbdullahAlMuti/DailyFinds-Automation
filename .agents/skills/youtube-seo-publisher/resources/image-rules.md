# Image Generation Rules & Prompt Engineering

All images must be generated using Antigravity's native `generate_image` tool.

## Technical Specifications
- **Featured Image**: 16:9 aspect ratio, high resolution (compressed to ≤1200px width WEBP/JPEG, <150KB for upload).
- **Supporting Images**: 16:9 aspect ratio, max 2 supporting images per article.
- **Filenames**: Hyphenated, descriptive, lower-case (`primary-keyword-featured.webp`, `topic-step-one.webp`).

## Prompt Guidelines
- **Style**: Editorial photography, clean realistic aesthetic, soft natural lighting.
- **Negative Constraints**:
  - NO embedded text, typography, titles, or floating words.
  - NO brand logos, trademarks, or copyrighted symbols.
  - NO recognizable celebrity or public figure likenesses without authorization.
  - NO glossy AI art clichés or distorted hands/faces.

## Manifest Requirement
Every generated image must be recorded in `outputs/<VIDEO_ID>/images/image-manifest.json` with:
- File path
- Intended placement (`featured`, `supporting-1`, `supporting-2`)
- Detailed generation prompt
- Alt text
- Caption
- Suggested filename
- AI-generated flag (`true`)
