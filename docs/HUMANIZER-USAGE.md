# Humanizer & SEO Article Humanizer Usage Guide

This guide details how to operate the installed `humanizer` skill and `seo-article-humanizer` orchestration skill in Antigravity 2.0.

---

## 1. System Overview

The humanization system consists of two complementary skills:
1. **Core Humanizer Skill** (`.agents/skills/humanizer/SKILL.md`): Detects 53 AI writing patterns, calculates pattern density scores (0–100), and applies 5 distinct human voice profiles (`casual`, `professional`, `technical`, `warm`, `blunt`).
2. **SEO Article Humanizer Orchestrator** (`.agents/skills/seo-article-humanizer/SKILL.md`): Manages the 13-stage editorial workflow for SEO articles, preserving facts, citations, links, keywords, schema, and WordPress Gutenberg block markup.

---

## 2. Score Interpretation Guidelines

- **What the Score Is**: An internal editorial metric measuring AI writing pattern density (repetitive structures, cliché transition words, uniform sentence cadence, generic intros).
- **What the Score Is NOT**:
  - NOT a Turnitin, GPTZero, or Originality.ai score.
  - NOT a proof of human or machine authorship.
  - NOT a direct Google ranking factor or AdSense rule.
- **Primary Goal**: Improve writing readability, flow, and human engagement—NOT detector evasion.

---

## 3. Installation & Security Summary

- **Primary Repository**: `https://github.com/Aboudjem/humanizer-skill`
- **Installed Path**: `.agents/skills/humanizer/`
- **Orchestration Path**: `.agents/skills/seo-article-humanizer/SKILL.md`
- **Security Audit Result**: Passed (100% offline Markdown, zero dependencies, zero network requests, zero secret requirements).
- **License**: MIT License.

---

## 4. How to Invoke Skills in Antigravity

### Reloading & Discovering Skills
Antigravity automatically discovers skills in `.agents/skills/`. To view active skills in conversation:
- Ask: `"List all installed project skills"` or `"Show available skills"`.

### Running Detect-Only Audit
To score an article without modifying text:
```text
Use humanizer --mode detect --score --file outputs/my-article/article/article.md --ignore-code --ignore-quotes
```

### Running Full Humanization Pipeline
To run the full 13-stage SEO humanization sequence:
```text
Use the seo-article-humanizer skill to audit and humanize outputs/my-article/article/article.md with primary keyword "my keyword"
```

---

## 5. Processing Markdown vs. HTML Content

- **Markdown Files (`article.md`)**: Analyzed for headings, lists, inline links, and code blocks.
- **WordPress HTML (`article.html`)**: Preserves Gutenberg comments (`<!-- wp:... -->`), `<figure class="wp-block-image">` blocks, HTML tables, and media URLs.

---

## 6. Protection Protocols

- **Protected Elements**: All facts, proper names, dates, numbers, citations, URLs, blockquotes, JSON-LD schema, and image references are stored in `protected-elements.json` before rewriting and verified after rewriting.
- **Zero Falsification**: The system strictly prohibits inserting fake personal stories, fake experience claims, fake quotes, or deliberate typos.

---

## 7. Output Directory Structure

For every processed article slug, the system outputs:

```text
outputs/<article-slug>/humanization/
├── article-original.md
├── article-humanized.md
├── article-original.html        (if source is HTML)
├── article-humanized.html       (if source is HTML)
├── protected-elements.json
├── humanization-audit-before.md
├── humanization-audit-after.md
├── humanization-change-log.md
└── final-humanization-report.md
```

---

## 8. Common Errors & Manual Review Checklist

- **High Remaining Score**: If technical articles retain necessary terminology, verify whether the score reflects necessary domain jargon rather than AI slop.
- **Manual Review Checklist**:
  1. Confirm `protected-elements.json` matches original values.
  2. Verify all internal/external links remain valid.
  3. Ensure no false first-person claims were added.
  4. Verify WordPress block HTML renders without syntax errors.
