"""
Content Package Directory Manager.
Creates and manages standard job output directory structure under outputs/<video-id>/.
"""

import os
import shutil
import json
import sys
from typing import Dict, Any
import yaml

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.utilities import logger


def init_content_package(video_id: str, base_output_dir: str = "outputs") -> str:
    """
    Initializes the required directory structure for a specific job under outputs/<video_id>/.
    Returns the absolute path to the package directory.
    """
    package_dir = os.path.abspath(os.path.join(base_output_dir, video_id))
    subfolders = ["source", "transcript", "research", "seo", "article", "images", "wordpress", "logs"]

    for sub in subfolders:
        os.makedirs(os.path.join(package_dir, sub), exist_ok=True)

    logger.info(f"Initialized content package directory structure at: {package_dir}")
    return package_dir


def save_resolved_job(package_dir: str, resolved_job_config: Dict[str, Any]) -> str:
    """Saves resolved job configuration YAML in the package directory."""
    job_path = os.path.join(package_dir, "job-resolved.yaml")
    with open(job_path, "w", encoding="utf-8") as f:
        yaml.dump(resolved_job_config, f, default_flow_style=False, sort_keys=False)
    logger.info(f"Saved resolved job configuration to {job_path}")
    return job_path


def load_package_metadata(package_dir: str) -> Dict[str, Any]:
    """Loads all existing package metadata across subdirectories if available."""
    meta = {"package_dir": package_dir}

    source_meta_path = os.path.join(package_dir, "source", "metadata.json")
    if os.path.exists(source_meta_path):
        with open(source_meta_path, "r", encoding="utf-8") as f:
            meta["source"] = json.load(f)

    ts_meta_path = os.path.join(package_dir, "transcript", "transcript-metadata.json")
    if os.path.exists(ts_meta_path):
        with open(ts_meta_path, "r", encoding="utf-8") as f:
            meta["transcript"] = json.load(f)

    job_yaml_path = os.path.join(package_dir, "job-resolved.yaml")
    if os.path.exists(job_yaml_path):
        with open(job_yaml_path, "r", encoding="utf-8") as f:
            meta["job"] = yaml.safe_load(f)

    return meta
