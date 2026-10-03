from PIL import Image
import os

photos_dir = "fcc_photos"
for f in sorted(os.listdir(photos_dir)):
    if f.endswith((".png", ".jpg")):
        p = os.path.join(photos_dir, f)
        sz = os.path.getsize(p)
        if sz > 100000:
            im = Image.open(p)
            print(f"{f:<30} {im.size} mode={im.mode} sz={sz/(1024):.1f}KB")
