from PIL import Image
import os

for f in sorted(os.listdir("fcc_photos")):
    if f.endswith(".jpg") and f.startswith("p1_"):
        im = Image.open(f"fcc_photos/{f}")
        print(f"{f}: {im.size}")
