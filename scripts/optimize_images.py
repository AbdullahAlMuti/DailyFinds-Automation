import os
import argparse
from PIL import Image

MAX_FILE_SIZE_KB = 150

def optimize_file(file_path):
    """Optimizes an existing image file in-place if it exceeds size thresholds."""
    if not os.path.exists(file_path):
        print(f"[FAIL] File not found: {file_path}")
        return False

    initial_size_kb = os.path.getsize(file_path) / 1024.0
    if initial_size_kb <= MAX_FILE_SIZE_KB:
        print(f"[OK] File already optimal: {file_path} ({initial_size_kb:.1f} KB)")
        return True

    ext = os.path.splitext(file_path)[1].lower()
    with Image.open(file_path) as img:
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        for quality in range(78, 50, -5):
            save_kwargs = {"optimize": True, "quality": quality}
            if ext in (".jpg", ".jpeg"):
                save_kwargs["progressive"] = True
                fmt = "JPEG"
            elif ext == ".webp":
                fmt = "WEBP"
            else:
                break

            img.save(file_path, format=fmt, **save_kwargs)
            new_size_kb = os.path.getsize(file_path) / 1024.0
            if new_size_kb <= MAX_FILE_SIZE_KB:
                print(f"[OK] Compressed {file_path} from {initial_size_kb:.1f} KB to {new_size_kb:.1f} KB (quality={quality})")
                return True

    final_size_kb = os.path.getsize(file_path) / 1024.0
    print(f"[WARN] Compressed {file_path} to {final_size_kb:.1f} KB")
    return True

def main():
    parser = argparse.ArgumentParser(description="Post Image Studio - Image Optimizer")
    parser.add_argument("--path", required=True, help="Image file or directory to optimize")
    args = parser.parse_args()

    if os.path.isdir(args.path):
        for root, _, files in os.walk(args.path):
            for f in files:
                if f.lower().endswith((".jpg", ".jpeg", ".webp", ".png")):
                    optimize_file(os.path.join(root, f))
    else:
        optimize_file(args.path)

if __name__ == "__main__":
    main()
