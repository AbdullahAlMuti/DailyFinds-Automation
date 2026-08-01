# YouTube-to-WordPress SEO Agent (`youtube-seo-wordpress-agent`)

A production-ready Antigravity 2.0 workflow and CLI tool suite that converts YouTube video URLs into thoroughly researched, original, SEO-optimized WordPress articles for **DailyFindz.com**.

> [!IMPORTANT]
> **Zero External Gemini API Key Required**: This project relies exclusively on Antigravity's native `generate_image` tool and local Python utilities. No `GEMINI_API_KEY` is required, requested, or stored.

> [!IMPORTANT]
> **DailyFindz Policy Alignment**:
> 1. **No Fabricated First-Person Experiences**: Third-party video content is converted into original synthesis guides rather than fake personal anecdotes ("I bought this and tested it").
> 2. **Monetization Guardrail**: Affiliate links remain strictly **disabled/paused** sitewide per DailyFindz pre-AdSense guidelines.
> 3. **Publication Safety Tri-Lock**: All posts default to `draft`. Public publishing requires 3-way agreement: `job.yaml` setting `status: publish`, `.env` setting `WP_ALLOW_PUBLICATION=true`, and CLI flag `--allow-publish`. Sensitive topics force draft mode automatically.

---

## 1. Features & Architecture

- **4-Tier Transcript Engine**:
  1. Local file upload (`.txt`, `.vtt`, `.srt`, `.json`)
  2. Creator-provided captions (`yt-dlp`)
  3. Automatic captions (`yt-dlp`, flagged as machine-generated)
  4. Permission-gated local speech-to-text (`faster-whisper` + `ffmpeg`)
- **Deterministic Python Processing**: Metadata extraction, caption cleaning, package scaffolding, quality checking, and WordPress REST API interactions.
- **Antigravity Reasoning & Generation**: Web research, claim verification, search-intent analysis, keyword planning, article writing, and native image generation (`generate_image`).
- **Quality Gates**: Blocking checks (missing transcript, incomplete content, placeholder text, low word count, unsafe HTML) and non-blocking warnings.
- **WordPress Integration**: Basic Authentication with Application Passwords (strictly redacted in logs), category/tag auto-creation, media upload with alt text, draft creation, read-back verification, and duplicate post protection.

---

## 2. Requirements & Setup

### System Requirements
- Python 3.9+
- FFmpeg (required only for Tier 4 local audio transcription)
- WordPress Site (`https://dailyfindz.com`) with REST API enabled and Application Passwords support.

### Installation

#### Windows PowerShell:
```powershell
# Clone or navigate to workspace
cd "d:\eBay Software\DailyFindz"

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install core dependencies
pip install -r requirements.txt
```

#### macOS / Linux:
```bash
cd youtube-seo-wordpress-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 3. WordPress Setup & Application Passwords

1. Log into WordPress Admin (`wp-admin`).
2. Go to **Users -> Profile**.
3. Scroll down to **Application Passwords**.
4. Enter `antigravity-publisher` and click **Add New Application Password**.
5. Copy the generated 24-character password (`xxxx xxxx xxxx xxxx xxxx xxxx`).
6. Copy `.env.example` to `.env` and fill in your credentials:

```ini
WP_BASE_URL=https://dailyfindz.com
WP_USERNAME=antigravity-publisher
WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx

WP_DEFAULT_STATUS=draft
WP_ALLOW_PUBLICATION=false
WP_REQUEST_TIMEOUT=30
WP_VERIFY_SSL=true

LOG_LEVEL=INFO
OUTPUT_DIRECTORY=outputs
```

> [!CAUTION]
> Never commit `.env` or print the complete WordPress Application Password in logs or reports.

---

## 4. Usage & Execution Walkthrough

### Test WordPress Connection
Verify credentials without creating any content:
```powershell
python scripts/main.py wordpress-test
```

### Step 1: Validate Job Configuration
```powershell
python scripts/main.py validate --job config/job.example.yaml
```

### Step 2: Prepare Package & Acquire Transcript
```powershell
python scripts/main.py prepare --job config/job.example.yaml
```
*Outputs created in `outputs/<VIDEO_ID>/`.*

### Step 3: Antigravity Research & Writing Phase
Prompt the Antigravity agent:
> "Process the content package in `outputs/<VIDEO_ID>` using the `youtube-seo-publisher` skill. Conduct web research for factual claims, write `article.md` and `article.html`, and generate featured and supporting images using `generate_image`."

### Step 4: Run Quality Checks
```powershell
python scripts/main.py check --package outputs/<VIDEO_ID>
```

### Step 5: Create WordPress Draft
```powershell
# Dry-run mode (simulates operation without HTTP calls):
python scripts/main.py wordpress-draft --package outputs/<VIDEO_ID> --dry-run

# Real Draft Creation:
python scripts/main.py wordpress-draft --package outputs/<VIDEO_ID>
```

### Step 6: Public Publication (Requires Safety Tri-Lock)
To publish publicly, all three controls must agree:
1. `config/job.yaml`: `wordpress.status: "publish"`
2. `.env`: `WP_ALLOW_PUBLICATION=true`
3. CLI Command:
```powershell
python scripts/main.py wordpress-publish --package outputs/<VIDEO_ID> --allow-publish
```

---

## 5. DailyFindz Categories

| Category Name | Category Slug | Term ID |
|---|---|---|
| Home & Kitchen | `home-kitchen` | 3 |
| Electronics | `electronics` | 4 |
| Beauty | `beauty` | 5 |
| Gadgets | `gadgets` | 6 |

---

## 6. Running Tests

Execute the complete pytest suite:
```powershell
pytest tests/ -v
```

---

## 7. Troubleshooting & Host Notes

- **Hostinger WAF 502 Rate Limits**: Hostinger WAF can intermittently return 502 Bad Gateway if media uploads are sent too quickly. The script processes images sequentially.
- **Rank Math / Yoast SEO Fields**: If SEO plugin REST fields are not exposed, the script creates the draft, saves intended SEO titles/meta descriptions in `report.md`, and notifies the user for manual entry.
