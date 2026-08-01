"""
4-Tier Transcript Acquisition Engine.
Tier 1: Existing local file (.txt, .vtt, .srt, .json)
Tier 2: Creator-provided captions (yt-dlp)
Tier 3: Automatic captions (yt-dlp, machine-generated flag)
Tier 4: Local Whisper transcription (permission-gated)
"""

import os
import json
import glob
import sys
from typing import Dict, Any, Optional, Tuple
import yt_dlp

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.utilities import logger


def acquire_transcript(
    video_id: str,
    video_url: str,
    output_dir: str,
    transcription_config: Dict[str, Any]
) -> Tuple[str, Dict[str, Any]]:
    """
    Executes the 4-tier transcript acquisition workflow.
    Returns a tuple of (raw_transcript_content, metadata_dict).
    """
    preferred_lang = transcription_config.get("preferred_language", "en")
    accept_creator = transcription_config.get("accept_creator_captions", True)
    accept_auto = transcription_config.get("accept_auto_captions", True)
    permit_audio = transcription_config.get("permit_audio_download", False)
    permit_local = transcription_config.get("permit_local_transcription", False)

    transcript_folder = os.path.join(output_dir, "transcript")
    os.makedirs(transcript_folder, exist_ok=True)

    # ---------------------------------------------------------
    # Tier 1: Check for existing transcript file in transcript_folder
    # ---------------------------------------------------------
    for ext in ["txt", "vtt", "srt", "json"]:
        matches = glob.glob(os.path.join(transcript_folder, f"transcript-original.{ext}"))
        if not matches:
            matches = glob.glob(os.path.join(transcript_folder, f"*.{ext}"))
            # Exclude clean or timestamped files
            matches = [m for m in matches if "clean" not in os.path.basename(m) and "timestamped" not in os.path.basename(m)]

        if matches:
            existing_file = matches[0]
            logger.info(f"[Tier 1] Found existing transcript file: {existing_file}")
            with open(existing_file, "r", encoding="utf-8") as f:
                content = f.read()

            meta = {
                "tier": "Tier 1 - Existing Local File",
                "source_file": existing_file,
                "language": preferred_lang,
                "is_machine_generated": False,
                "method": "local_file"
            }
            return content, meta

    # ---------------------------------------------------------
    # Tier 2: Creator-Provided Captions via yt-dlp
    # ---------------------------------------------------------
    if accept_creator:
        logger.info(f"[Tier 2] Attempting to download creator captions for language '{preferred_lang}'")
        content, caption_type = _download_yt_captions(video_url, transcript_folder, preferred_lang, auto=False)
        if content:
            meta = {
                "tier": "Tier 2 - Creator Captions",
                "language": preferred_lang,
                "is_machine_generated": False,
                "caption_format": caption_type,
                "method": "yt_dlp_creator"
            }
            return content, meta

    # ---------------------------------------------------------
    # Tier 3: Automatic Captions via yt-dlp
    # ---------------------------------------------------------
    if accept_auto:
        logger.info(f"[Tier 3] Creator captions unavailable. Attempting auto-captions for '{preferred_lang}'")
        content, caption_type = _download_yt_captions(video_url, transcript_folder, preferred_lang, auto=True)
        if content:
            meta = {
                "tier": "Tier 3 - Automatic Captions",
                "language": preferred_lang,
                "is_machine_generated": True,
                "caption_format": caption_type,
                "method": "yt_dlp_auto"
            }
            return content, meta

    # ---------------------------------------------------------
    # Tier 4: Local Speech-To-Text (Whisper / faster-whisper)
    # ---------------------------------------------------------
    if permit_audio and permit_local:
        logger.info("[Tier 4] Attempting local audio download and transcription via faster-whisper")
        content, meta = _transcribe_audio_locally(video_url, transcript_folder, transcription_config)
        if content:
            return content, meta

    # ---------------------------------------------------------
    # Fallback / Failure
    # ---------------------------------------------------------
    raise RuntimeError(
        f"No transcript could be acquired for video {video_id}. "
        "Creator and auto captions were not found or disabled, and local transcription is not permitted. "
        f"Please manually place a transcript file in '{transcript_folder}/transcript-original.txt'."
    )


def _download_yt_captions(
    video_url: str,
    output_folder: str,
    lang: str,
    auto: bool = False
) -> Tuple[Optional[str], Optional[str]]:
    """Helper to download VTT subtitles using yt-dlp."""
    output_template = os.path.join(output_folder, "transcript-original")
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': not auto,
        'writeautomaticsub': auto,
        'subtitleslangs': [lang, 'en'],
        'subtitlesformat': 'vtt/srt/best',
        'outtmpl': output_template,
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        # Search downloaded subtitle file
        downloaded = glob.glob(os.path.join(output_folder, "transcript-original*.*"))
        for fpath in downloaded:
            if fpath.endswith((".vtt", ".srt")):
                ext = fpath.split(".")[-1]
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
                return content, ext
    except Exception as e:
        logger.warning(f"yt-dlp subtitle download exception: {e}")

    return None, None


def _transcribe_audio_locally(
    video_url: str,
    output_folder: str,
    transcription_config: Dict[str, Any]
) -> Tuple[Optional[str], Dict[str, Any]]:
    """Helper to download audio and transcribe via faster-whisper if installed."""
    model_size = transcription_config.get("whisper_model", "small")
    audio_path = os.path.join(output_folder, "audio.m4a")

    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'outtmpl': audio_path,
        'quiet': True,
        'no_warnings': True,
    }

    try:
        logger.info(f"Downloading audio stream for local transcription...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        try:
            from faster_whisper import WhisperModel
            logger.info(f"Loading faster-whisper model '{model_size}'...")
            model = WhisperModel(model_size, device="cpu", compute_type="int8")
            segments, info = model.transcribe(audio_path, beam_size=5)

            transcript_lines = []
            for segment in segments:
                transcript_lines.append(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text.strip()}")

            full_text = "\n".join(transcript_lines)
            save_path = os.path.join(output_folder, "transcript-original.txt")
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(full_text)

            meta = {
                "tier": "Tier 4 - Local Speech-To-Text",
                "whisper_model": model_size,
                "detected_language": info.language,
                "is_machine_generated": True,
                "method": "faster_whisper"
            }
            return full_text, meta

        except ImportError:
            logger.error("faster-whisper library is not installed. Install with `pip install faster-whisper` for Tier 4 support.")
            return None, {}

    except Exception as e:
        logger.error(f"Local audio transcription failed: {e}")
        return None, {}
    finally:
        if os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except Exception:
                pass
