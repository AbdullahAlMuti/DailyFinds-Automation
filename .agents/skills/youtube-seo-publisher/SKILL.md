---
name: youtube-seo-publisher
description: Converts authorized YouTube videos into researched, original, SEO-friendly WordPress articles with Antigravity-generated images and controlled publishing.
---

# YouTube to WordPress SEO Publisher Skill

This skill guides the Antigravity Agent and python automation scripts to process a YouTube video URL into a fully researched, SEO-optimized, image-rich WordPress draft or article for DailyFindz.com.

## Pipeline Responsibilities

### Python Script Responsibilities (Deterministic Execution)
1. **Configuration Validation**: Validate job YAML against settings and environment using `scripts/main.py validate`.
2. **YouTube Extraction**: Retrieve video metadata (title, duration, channel, description, thumbnail) using `scripts/youtube_source.py`.
3. **Transcript Acquisition & Cleanup**: Execute 4-tier transcript engine (Local file -> Creator captions -> Auto captions -> Gated Whisper) via `scripts/transcript.py` and clean it with `scripts/transcript_cleaner.py`.
4. **Content Package Init**: Scaffold `outputs/<VIDEO_ID>/` directories via `scripts/content_package.py`.
5. **Quality Gate Validation**: Run blocking and non-blocking quality checks using `scripts/quality_checker.py`.
6. **WordPress REST Operations**: Handle authentication check, category/tag resolution, media upload with alt text, draft creation, read-back verification, and duplicate checks via `scripts/wordpress_client.py`.

### Antigravity Agent Responsibilities (Creative & Analytical Reasoning)
1. **Topic & Claim Extraction**: Review `transcript-clean.txt` and `transcript-timestamped.md`. Extract key claims, terminology, and main concepts into `claim-check.md`.
2. **Web Research**: Use browser search capabilities to verify claims against current authoritative sources. Document findings in `research-notes.md` and `sources.json`.
3. **SEO Strategy**: Conduct search-intent analysis, select primary and secondary long-tail keywords, and write `seo-brief.md`.
4. **Article Composition**: Write `article.md` and WordPress block-editor compatible `article.html` following DailyFindz brand rules (no fabricated experience, no affiliate links, clear H2/H3 structure, single H1).
5. **Image Generation**: Use native `generate_image` tool to create 1 featured image (16:9) and supporting images (16:9). Save metadata in `image-manifest.json` and prompts in `image-prompts.md`.
6. **Final Report Generation**: Generate `final-report.md` summarizing the job execution, quality status, WordPress post ID, and required manual actions.

---

## Step-by-Step Execution Walkthrough

### Step 1: Initialize and Validate Job
Run job validation:
```bash
python scripts/main.py validate --job config/job.yaml
```

### Step 2: Prepare Package & Acquire Transcript
Execute package preparation:
```bash
python scripts/main.py prepare --job config/job.yaml
```
Output files created in `outputs/<VIDEO_ID>/`:
- `source/metadata.json`
- `transcript/transcript-original.*`
- `transcript/transcript-clean.txt`
- `transcript/transcript-timestamped.md`
- `transcript/transcript-metadata.json`

### Step 3: Conduct Research & Fact Checking
1. Read `outputs/<VIDEO_ID>/transcript/transcript-clean.txt`.
2. Identify core factual claims (prices, specs, techniques, stats).
3. Search current web sources for authoritative verification.
4. Write `outputs/<VIDEO_ID>/research/research-notes.md`, `sources.json`, and `claim-check.md`.

### Step 4: SEO Planning & Article Writing
1. Create `outputs/<VIDEO_ID>/seo/seo-brief.md`.
2. Write `outputs/<VIDEO_ID>/article/article.md` and `outputs/<VIDEO_ID>/article/article.html`.
   - Adhere strictly to `.agents/skills/youtube-seo-publisher/resources/article-template.md`.
   - Enforce DailyFindz rules: honest tone, single H1, long-tail target keyword in H1, intro, slug, and meta description (excerpt).
   - If third-party video: synthesize without fake first-person claims ("I bought/tested").

### Step 5: Native Image Generation
1. Formulate prompts in `outputs/<VIDEO_ID>/images/image-prompts.md` using `.agents/skills/youtube-seo-publisher/resources/image-rules.md`.
2. **MANDATORY**: Do NOT embed YouTube videos, iframes, or oEmbed blocks anywhere in the article. Replace all video references with generated images.
3. Call `generate_image` tool for the **featured image** (1 image):
   - Aspect ratio: `16:9`
   - Prompt: Realistic, professional editorial photography. No text inside image, no brand logos.
   - Save to `outputs/<VIDEO_ID>/images/primary-keyword-featured-image.webp`.
4. Call `generate_image` tool for **inline supporting images** — generate a **minimum of 4, up to 9** (total **5–10** images including featured). This is required for AdSense approval:
   - Each image must represent a distinct section/concept of the article.
   - Distribute evenly: aim for one image per every 2 H2 sections.
   - Aspect ratio: `16:9` for each.
   - Name sequentially: `inline-1.webp`, `inline-2.webp`, … `inline-9.webp`.
5. Save all metadata into `outputs/<VIDEO_ID>/images/image-manifest.json` with placement keys `featured`, `inline-1` through `inline-9`.

### Resource Files
- [.agents/skills/youtube-seo-publisher/resources/dailyfindz-brand-rules.md](file:///d:/eBay%20Software/DailyFindz/.agents/skills/youtube-seo-publisher/resources/dailyfindz-brand-rules.md): Brand colors, voice, author guidelines, and paused affiliate rules.
- [.agents/skills/youtube-seo-publisher/resources/article-template.md](file:///d:/eBay%20Software/DailyFindz/.agents/skills/youtube-seo-publisher/resources/article-template.md): Block-editor structure template.
- [.agents/skills/youtube-seo-publisher/resources/seo-checklist.md](file:///d:/eBay%20Software/DailyFindz/.agents/resources/seo-checklist.md): Search intent and keyword placement rules.
- [.agents/skills/youtube-seo-publisher/resources/research-rules.md](file:///d:/eBay%20Software/DailyFindz/.agents/resources/research-rules.md): Fact checking and claim verification rules.
- [.agents/skills/youtube-seo-publisher/resources/image-rules.md](file:///d:/eBay%20Software/DailyFindz/.agents/resources/image-rules.md): Generative image prompt rules.
- [.agents/skills/youtube-seo-publisher/resources/wordpress-rules.md](file:///d:/eBay%20Software/DailyFindz/.agents/resources/wordpress-rules.md): REST API category mapping and safety locks.

### Step 6: Quality Gate Check
Run the quality checker:
```bash
python scripts/main.py check --package outputs/<VIDEO_ID>
```
Verify that `outputs/<VIDEO_ID>/quality-report.json` passes all blocking checks.

### Step 7: WordPress Upload & Read-Back Verification
1. Test connection first if needed:
   ```bash
   python scripts/main.py wordpress-test
   ```
2. Create WordPress Draft (or Publish if tri-lock satisfied):
   ```bash
   python scripts/main.py wordpress-draft --package outputs/<VIDEO_ID>
   ```
3. For dry-run mode without network calls:
   ```bash
   python scripts/main.py wordpress-draft --package outputs/<VIDEO_ID> --dry-run
   ```

### Step 8: Produce Final Execution Report
Generate `outputs/<VIDEO_ID>/final-report.md` summarizing:
- Video ID, Title, Channel
- Word count, Keywords, Intent
- Generated Image paths & Alt text
- WordPress Post ID, Status, Read-back verification
- Quality check status and warnings
