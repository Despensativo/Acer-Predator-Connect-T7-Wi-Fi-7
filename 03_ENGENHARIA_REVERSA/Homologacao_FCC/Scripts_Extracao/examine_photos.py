from PIL import Image
import os

# Let us check the aspect ratio and colors of the images
for f in sorted(os.listdir("fcc_photos")):
    if f.endswith((".jpg", ".png")) and not f.endswith("Im0.png"):
        im = Image.open(f"fcc_photos/{f}")
        # Crop center and save a thumbnail
        w, h = im.size
        print(f"{f}: {w}x{h}")
