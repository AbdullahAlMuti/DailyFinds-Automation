import os
import requests

def test_fetch():
    target_dir = "outputs/z2QLALwNwQw/images"
    os.makedirs(target_dir, exist_ok=True)

    # High-resolution photorealistic stock image URLs matching our 4 slots:
    image_urls = {
        "featured.jpg": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=1600&h=900&q=80",
        "inline1.jpg": "https://images.unsplash.com/photo-1531403009284-440f080d1e12?auto=format&fit=crop&w=1600&h=900&q=80",
        "inline2.jpg": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=1600&h=900&q=80",
        "inline3.jpg": "https://images.unsplash.com/photo-1551836022-d5d88e9218df?auto=format&fit=crop&w=1600&h=900&q=80"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for name, url in image_urls.items():
        dst = os.path.join(target_dir, name)
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code == 200:
            with open(dst, "wb") as f:
                f.write(res.content)
            print(f"[OK] Downloaded photorealistic image: {dst} ({len(res.content)} bytes)")
        else:
            print(f"❌ Failed to download {name}, status: {res.status_code}")

if __name__ == "__main__":
    test_fetch()
