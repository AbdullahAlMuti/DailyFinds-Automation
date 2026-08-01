---
name: world-class-seo-article
description: Orchestrates an end-to-end SEO article workflow from YouTube transcripts using Aaron Marketing skills (keyword research, SERP analysis, content gap, content writing, GEO optimization, JSON-LD schema, quality audit, and on-page SEO). Outputs a verified WordPress draft.
---

# World-Class SEO Article Orchestrator

An Antigravity 2.0 orchestration skill that turns raw YouTube transcripts into original, highly-ranked, authoritative SEO articles using Aaron Marketing skills.

---

## Workflow Execution Sequence

### Phase 1: Transcript & Intent Analysis
1. Read the clean YouTube transcript from `outputs/<video-id>/transcript/transcript-clean.txt`.
2. Extract core topics, named entities, target audience pain points, and specific questions answered in the video.

### Phase 2: SEO & Competitor Research
3. **Keyword Research (`keyword-research`)**:
   - Determine primary and secondary keywords.
   - Use web search for search intent mapping.
   - *Rule*: Never invent volume or traffic numbers; mark missing metrics as `unknown`. Zero paid API required.
4. **SERP Analysis (`serp-analysis`)**:
   - Perform live search queries to observe current top-ranking structures, featured snippet formats, and People Also Ask questions.
5. **Content Gap Analysis (`content-gap-analysis`)**:
   - Identify missing depth, unanswered questions, or outdated claims in existing SERP results.
6. **Content Brief**:
   - Synthesize findings into a structured Content Brief (`content-brief.md`).

### Phase 3: Drafting & Fact Verification
7. **Content Writer (`content-writer`)**:
   - Draft article in new-content mode.
   - *Writing Rules*: Write for humans first; satisfy intent in the opening paragraphs; add original value beyond the video transcript; properly attribute the video; no keyword stuffing; no fabricated experiences, statistics, or fake studies; no generic AI intros or conclusions.
8. **Fact Verification**:
   - Verify all material factual claims using authoritative live web sources (`search_web` / `read_url_content`).

### Phase 4: Optimization & Markup
9. **Generative Engine Optimization (`geo-content-optimizer`)**:
   - Structure direct answer blocks, bullet summaries, and entity definitions for AI search engines (Perplexity, Gemini, ChatGPT search).
10. **Schema Markup (`serp-markup-builder`)**:
    - Generate validated `BlogPosting` JSON-LD and `FAQPage` JSON-LD schema.

### Phase 5: Quality Audit & Loop
11. **Content Quality Auditor (`content-quality-auditor`)**:
    - Evaluate readability, fluff, structural clarity, and source attribution.
    - **Audit Loop**: If the auditor returns `FIX`, return to `content-writer` for revisions and re-audit until status is `PASS`.
12. **On-Page SEO Checker (`on-page-seo-checker`)**:
    - Verify H1 single usage, meta description length, keyword density, alt text presence, and heading hierarchy.

### Phase 6: Media & WordPress Draft
13. **Image Generation & Manifest**:
    - Generate 16:9 featured image and supporting images via Antigravity's native `generate_image` tool.
    - Record prompts, filenames, alt text, and captions in `image-manifest.json`.
14. **WordPress Draft Creation**:
    - Upload media to WordPress Media Library.
    - Create post in **Draft mode** (`status: draft`).
    - *Publication Rule*: The WordPress post MUST remain a draft unless explicitly authorized by user for public publication.

---

## Required Article Package Outputs

Every execution must create `outputs/<video-id>/` containing:

1. `source/metadata.json` & `transcript/transcript-clean.txt`
2. `seo/content-brief.md`
3. `seo/schema.json` (BlogPosting & FAQPage JSON-LD)
4. `article/article.md` & `article/article.html`
5. `images/image-manifest.json` + `images/*.jpg`
6. `quality-report.json` & `transcription-report.md`

---

## Zero API Key & Data Integrity Guarantee
- Uses native browser research (`search_web`, `read_url_content`) for live web facts.
- No Ahrefs, Semrush, Gemini, or OpenAI API keys are required or requested.
- Unavailable metrics are explicitly marked `unknown`.
