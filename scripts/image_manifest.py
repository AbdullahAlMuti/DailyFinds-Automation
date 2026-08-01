import os
import json
import argparse
from PIL import Image

def generate_manifest_entry(original_path, resized_paths, placement, alt_text, caption, base_filename):
    """Creates a structured manifest record for an image and its resized variants."""
    with Image.open(original_path) as img:
        orig_w, orig_h = img.size
        orig_fmt = img.format

    variants = []
    for rpath in resized_paths:
        if os.path.exists(rpath):
            with Image.open(rpath) as rimg:
                rw, rh = rimg.size
                rfmt = rimg.format
                rsize = os.path.getsize(rpath)
            variants.append({
                "path": os.path.relpath(rpath).replace("\\", "/"),
                "width": rw,
                "height": rh,
                "format": rfmt,
                "size_bytes": rsize,
                "filename": os.path.basename(rpath)
            })

    entry = {
        "placement": placement,
        "base_filename": base_filename,
        "original": {
            "path": os.path.relpath(original_path).replace("\\", "/"),
            "width": orig_w,
            "height": orig_h,
            "format": orig_fmt,
            "size_bytes": os.path.getsize(original_path)
        },
        "alt_text": alt_text,
        "caption": caption,
        "variants": variants
    }
    return entry

def save_manifest(output_file, entries):
    """Saves manifest array to image-manifest.json."""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)
    print(f"[OK] Saved image manifest to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Post Image Studio - Manifest Builder")
    parser.add_argument("--output", required=True, help="Path to image-manifest.json")
    parser.add_argument("--entry-json", help="JSON string of a single manifest entry")
    args = parser.parse_args()

    entries = []
    if os.path.exists(args.output):
        try:
            with open(args.output, "r", encoding="utf-8") as f:
                entries = json.load(f)
        except Exception:
            entries = []

    if args.entry_json:
        new_entry = json.loads(args.entry_json)
        entries.append(new_entry)
        save_manifest(args.output, entries)

if __name__ == "__main__":
    main()
