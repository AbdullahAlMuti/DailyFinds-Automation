---
name: youtube-transcript
description: Download YouTube video transcripts when user provides a YouTube URL or asks to download/get/fetch a transcript from YouTube. Also use when user wants to transcribe or get captions/subtitles from a YouTube video.
---

# YouTube Transcript Skill for Antigravity 2.0

Acquires, cleans, and formats transcripts from YouTube videos using a 3-tier fallback strategy (Manual Captions → Auto-Captions → Local Whisper). Requires zero API keys.

## Processing Workflow & Priority Order

1. **URL Validation**: Verify YouTube URL format and extract the 11-character Video ID.
2. **Metadata Extraction**: Fetch title, channel, duration, and list available caption languages using `yt-dlp`.
3. **Caption Discovery**:
   - **Tier 1 (Preferred)**: Manually created creator subtitles (`yt-dlp --write-sub`).
   - **Tier 2**: Automatic YouTube captions (`yt-dlp --write-auto-sub`).
   - **Tier 3 (Local Fallback)**: Local Whisper transcription (`whisper` or `faster-whisper`) when no usable captions exist.
4. **Transcript Processing & Cleaning**:
   - Save original VTT subtitle file to `outputs/<video-id>/transcript-original.vtt`.
   - Strip WebVTT headers, timecode lines, and HTML tags (`<c>`, `<b>`, `<i>`).
   - Deduplicate scrolling/progressive overlapping caption lines.
   - Merge sentence fragments into clean readable paragraphs preserving paragraph order and meaning.
   - Preserve technical terminology, proper names, numbers, and timestamps.
   - Mark uncertain or low-confidence passages instead of inventing missing words.
5. **Report Generation**: Write `outputs/<video-id>/transcription-report.md` summarizing the method, language, duration, and output files.

---

## Output Structure

For each processed video, generate:

```text
outputs/<video-id>/
├── metadata.json
├── transcript-original.vtt
├── transcript-timestamped.md
├── transcript-clean.txt
└── transcription-report.md
```

---

## Command Reference

### Check Available Subtitles
```bash
yt-dlp --list-subs "YOUTUBE_URL"
```

### Tier 1: Download Manual Subtitles
```bash
yt-dlp --write-sub --sub-langs "en.*,en" --sub-format vtt --skip-download --output "outputs/VIDEO_ID/transcript-original.%(ext)s" "YOUTUBE_URL"
```

### Tier 2: Download Automatic Captions
```bash
yt-dlp --write-auto-sub --sub-langs "en.*,en" --sub-format vtt --skip-download --output "outputs/VIDEO_ID/transcript-original.%(ext)s" "YOUTUBE_URL"
```

### Tier 3: Local Whisper Fallback
When no subtitles are available, download authorized audio and transcribe locally:
```bash
# Extract Audio
yt-dlp --extract-audio --audio-format mp3 --output "outputs/VIDEO_ID/audio.%(ext)s" "YOUTUBE_URL"

# Transcribe locally with Whisper (default model: small)
whisper "outputs/VIDEO_ID/audio.mp3" --model small --output_dir "outputs/VIDEO_ID" --output_format all
```

*Note: Delete temporary `audio.mp3` after successful transcription unless job settings specify to preserve it.*

---

## Zero API Key Guarantee
This skill runs strictly using open tools (`yt-dlp`, `ffmpeg`, local `whisper`). No Gemini, OpenAI, or YouTube Data API keys are required or requested.
