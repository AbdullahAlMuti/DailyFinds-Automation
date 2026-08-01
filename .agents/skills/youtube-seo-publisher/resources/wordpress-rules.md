# WordPress REST API Rules for DailyFindz

## Authentication & Base URL
- Base URL: `https://dailyfindz.com`
- Authentication: HTTPS Basic Auth using `WP_USERNAME` and `WP_APP_PASSWORD`.
- Passwords MUST be masked as `[REDACTED]` in all output logs and artifacts.

## Category & Tag Mapping
DailyFindz standard categories:
| Category Name | Category Slug | Term ID |
|---|---|---|
| Home & Kitchen | `home-kitchen` | 3 |
| Electronics | `electronics` | 4 |
| Beauty | `beauty` | 5 |
| Gadgets | `gadgets` | 6 |

If a category name is provided in `job.yaml`, lookup term by name/slug or create it if absent.

## Post Status Guardrails
- **Default**: `draft`
- **Publishing Lock**: `status` can only be set to `publish` if:
  1. `job.wordpress.status` == `publish`
  2. `WP_ALLOW_PUBLICATION` == `true`
  3. CLI flag `--allow-publish` is passed
- If any lock condition fails, force status to `draft`.

## HTML Formatting Constraints
- Output block-editor compatible clean HTML (`article.html`).
- NO `<head>`, `<body>`, or full HTML page wrappers.
- NO `<script>`, inline JS event handlers (`onclick`), or unsafe `<iframe>` (except verified YouTube embed iframe).
- NO inline CSS styling block clutter.

## Duplicate Protection
- Before posting, query `/wp-json/wp/v2/posts?slug=<SLUG>`.
- If a post with the exact slug exists and policy is `stop`, halt execution.
