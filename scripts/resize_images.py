import os
import argparse
from PIL import Image, ImageOps

SIZE_PROFILES = {
    "featured": [
        {"width": 1600, "height": 900, "format": "WEBP", "ext": "webp"},
        {"width": 1200, "height": 630, "format": "JPEG", "ext": "jpg"},
        {"width": 768, "height": 432, "format": "WEBP", "ext": "webp"}
    ],
    "inline": [
        {"width": 1600, "height": 900, "format": "WEBP", "ext": "webp"},
        {"width": 1200, "height": 675, "format": "WEBP", "ext": "webp"}
    ],
    "social": [
        {"width": 1200, "height": 630, "format": "JPEG", "ext": "jpg"},
        {"width": 1080, "height": 1080, "format": "JPEG", "ext": "jpg"},
        {"width": 1080, "height": 1350, "format": "JPEG", "ext": "jpg"}
    ]
}

def resize_and_crop(image_path, target_width, target_height):
    """Resizes and crops an image to exact target dimensions using Pillow ImageOps.fit."""
    with Image.open(image_path) as img:
        # Convert RGBA to RGB for JPEG compatibility
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        resized = ImageOps.fit(img, (target_width, target_height), method=Image.Resampling.LANCZOS)
        return resized

def process_image(src_path, output_dir, base_name, placement):
    """Processes a single source image into all defined size profiles for its placement."""
    profiles = SIZE_PROFILES.get(placement, SIZE_PROFILES["inline"])
    os.makedirs(output_dir, exist_ok=True)
    generated_variants = []

    for prof in profiles:
        w, h, fmt, ext = prof["width"], prof["height"], prof["format"], prof["ext"]
        filename = f"{base_name}-{w}x{h}.{ext}"
        target_path = os.path.join(output_dir, filename)

        resized_img = resize_and_crop(src_path, w, h)
        
        save_kwargs = {"optimize": True}
        if fmt == "JPEG":
            save_kwargs["quality"] = 82
            save_kwargs["progressive"] = True
        elif fmt == "WEBP":
            save_kwargs["quality"] = 80
            
        resized_img.save(target_path, format=fmt, **save_kwargs)
        
        generated_variants.append({
            "path": target_path,
            "width": w,
            "height": h,
            "format": fmt,
            "ext": ext,
            "filename": filename
        })
        print(f"[OK] Generated variant: {target_path} ({w}x{h} {fmt})")
        
    return generated_variants

def main():
    parser = argparse.ArgumentParser(description="Post Image Studio - Image Resizer")
    parser.add_argument("--src", required=True, help="Path to original image")
    parser.add_argument("--output-dir", required=True, help="Directory to save resized variants")
    parser.add_argument("--name", required=True, help="Base slug filename (without ext)")
    parser.add_argument("--placement", choices=["featured", "inline", "social"], default="inline", help="Placement profile")
    args = parser.parse_args()

    process_image(args.src, args.output_dir, args.name, args.placement)

if __name__ == "__main__":
    main()
