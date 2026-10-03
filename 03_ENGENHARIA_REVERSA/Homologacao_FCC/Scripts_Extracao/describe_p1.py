import os
from PIL import Image

# Check average color in center of each image
for f in sorted(os.listdir("fcc_photos")):
    if f.startswith("p1_page") and f.endswith(".jpg"):
        im = Image.open(f"fcc_photos/{f}")
        w, h = im.size
        # sample 100 pixels in center
        center = im.crop((w//4, h//4, 3*w//4, 3*h//4))
        # get dominant colors
        colors = center.resize((1, 1)).getpixel((0, 0))
        print(f"{f}: size={w}x{h} center_rgb={colors}")
