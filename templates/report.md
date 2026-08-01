# YouTube-to-WordPress Execution Report

**Job ID**: `{{JOB_ID}}`
**Video ID**: `{{VIDEO_ID}}`
**Execution Date**: {{TIMESTAMP}}

---

## 1. Source Video Summary
- **Title**: {{VIDEO_TITLE}}
- **Channel**: {{CHANNEL_NAME}}
- **URL**: {{VIDEO_URL}}
- **Duration**: {{DURATION}}
- **Transcript Method**: {{TRANSCRIPT_METHOD}} (Language: {{TRANSCRIPT_LANG}})

---

## 2. Content & SEO Metrics
- **Article Title**: {{ARTICLE_TITLE}}
- **Primary Keyword**: `{{PRIMARY_KEYWORD}}`
- **Slug**: `{{SLUG}}`
- **Word Count**: {{WORD_COUNT}} words
- **Search Intent**: {{SEARCH_INTENT}}

---

## 3. Generated Images
| Image Type | Local File Path | Suggested Filename | Alt Text |
|---|---|---|---|
| Featured | `{{FEATURED_IMAGE_PATH}}` | `{{FEATURED_FILENAME}}` | {{FEATURED_ALT}} |
| Supporting 1 | `{{SUPPORTING_1_PATH}}` | `{{SUPPORTING_1_FILENAME}}` | {{SUPPORTING_1_ALT}} |
| Supporting 2 | `{{SUPPORTING_2_PATH}}` | `{{SUPPORTING_2_FILENAME}}` | {{SUPPORTING_2_ALT}} |

---

## 4. Quality Validation Status
- **Overall Status**: **{{QUALITY_PASS_FAIL}}**
- **Blocking Checks Passed**: {{BLOCKING_PASSED_COUNT}}/{{BLOCKING_TOTAL_COUNT}}
- **Warnings**: {{WARNINGS_COUNT}}
{{QUALITY_WARNINGS_LIST}}

---

## 5. WordPress Integration Status
- **Authentication**: {{WP_AUTH_STATUS}}
- **Target Category**: {{WP_CATEGORY}} (ID: {{WP_CATEGORY_ID}})
- **Assigned Tags**: {{WP_TAGS}}
- **Post ID**: `{{WP_POST_ID}}`
- **Assigned Status**: `{{WP_STATUS}}`
- **Read-Back Verification**: {{WP_READBACK_STATUS}}
- **SEO Plugin Status**: {{SEO_PLUGIN_STATUS}}

---

## 6. Required Manual Actions
{{MANUAL_ACTIONS_LIST}}
