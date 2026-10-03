import os
from PIL import Image

# Check which images are larger than 600KB and have green/blue/black PCB
for f in sorted(os.listdir("fcc_photos")):
    if f.endswith((".jpg", ".png")) and not f.endswith("Im0.png"):
        p = os.path.join("fcc_photos", f)
        sz = os.path.getsize(p)
        print(f"{f}: {sz} bytes")
