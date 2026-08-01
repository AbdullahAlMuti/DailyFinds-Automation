# Publishing Safety Rules

> [!IMPORTANT]
> These rules govern all content generation and WordPress publishing actions taken by the Antigravity Agent, subagents, and associated scripts.

## 1. WordPress Status & Publication Tri-Lock

- **Default Status**: The default WordPress status must ALWAYS be `draft`.
- **Public Publication**: Public publishing is strictly prohibited unless ALL THREE conditions are met simultaneously:
  1. `job.yaml` specifies `wordpress.status: "publish"`
  2. `.env` file specifies `WP_ALLOW_PUBLICATION=true`
  3. CLI invocation explicitly passes the `--allow-publish` flag.
- If any of these three conditions is missing, the system MUST force `status: draft`.

## 2. Sensitive Topic Lock

If an article touches on sensitive or high-impact topics, it MUST be forced to `draft` for human editorial review, regardless of publication flags:
- Medical or health advice
- Legal advice
- Financial advice or investment strategies
- Political persuasion or elections
- Allegations about identifiable living individuals (defamation risk)
- Emergency or public safety information
- Child safety, weapons, or self-harm

## 3. DailyFindz Editorial & Experience Integrity Rules

- **NO Fabricated Experience**: Never write a first-person ("I tried this", "I bought this") narrative based on someone else's video or content. That violates copyright, AdSense policy, and DailyFindz Editorial Policy.
  - If the content is from the site owner (Muti), first-person narrative is allowed.
  - If the content is from a third-party video, write an **original synthesis guide** citing sources, providing external research, and offering practical advice without fake personal claims.
- **Affiliate Link Pause**: Affiliate links are strictly **DISABLED sitewide** pending AdSense approval. Do NOT add affiliate links, product affiliate buttons, or affiliate disclosures to any post.
- **Comments**: Comments must be set to `closed` sitewide.

## 4. Secret Protection

- WordPress Application Passwords, authentication headers, cookies, and tokens MUST NEVER be printed in logs, debug output, test outputs, execution reports, or terminal stdout.
- Application passwords must be sanitized to `[REDACTED]` prior to logging.

## 5. Google AdSense Approval & World-Class Quality Standards

- **Primary Goal**: Absolute Maximum Quality, E-E-A-T AdSense Approval Standard.
- **Mandatory Word Count Range**: Every article MUST be between **3,000 and 3,500 words** of deep, highly descriptive, human-level editorial content. Word counts below 3,000 words are prohibited.
- **Mandatory 4 Context-Driven Educational Images**: Every post package MUST include 4 optimized images (1 Featured Hero Image + 3 Inline Educational Visual Diagrams) tailored specifically to explain section concepts visually.
- **Human-Written SEO Alt Text**: All image alt text must be written like a human SEO editor, incorporating target and secondary LSI keywords naturally while describing the visual accurately.
- **Mandatory E-E-A-T Author & Editorial Reviewer Box**: Every article must include clear author attribution and expert editorial review credentials for Google E-E-A-T verification.
- **Mandatory Pre-Draft Quality & AI Detection Gate**: Every post package MUST pass the automated AI content detector and quality validator (`scripts/quality_checker.py`) BEFORE creating or updating a WordPress draft.
- **Zero AI Slop / Zero Thin Content**: Never produce generic summaries or paragraph-by-paragraph transcript rewrites. Add substantial original research, web search verifications, structured Pros and Cons evaluation tables, and value beyond the video script.
- **Media Quality**: All post images must be generated natively via `post-image-studio`, optimized (<150KB WebP/JPEG), packaged with `image-manifest.json`, and uploaded directly into WordPress post content.
- **Rich Schema**: Include validated `BlogPosting` and `FAQPage` JSON-LD schema on every post package.

## 6. No Video Embeds Rule

- **NO YouTube Video Embeds**: Do NOT embed YouTube videos (`<iframe ...>`, video player embeds, or video links) inside the published HTML or Markdown article content.
- **ALWAYS Generate Original Educational Images**: Every article MUST generate and use 4 custom, high-quality visual images (1 Featured Hero Image + 3 Inline Educational Visual Diagrams) created natively via `generate_image` and processed through `post-image-studio`.



