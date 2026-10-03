import os
from PIL import Image

# In FCC filings, there are usually overview photos (wide shot with ruler)
# and close-up photos of individual chips (SoC, Flash, RAM, RF chips).
for f in sorted(os.listdir("fcc_photos")):
    if f.endswith((".jpg", ".png")):
        im = Image.open(f"fcc_photos/{f}")
        # check average brightness and variance
        print(f"{f}: {im.size}")
