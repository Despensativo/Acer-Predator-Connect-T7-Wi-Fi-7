import os
from PIL import Image

photos = [
    "p3_page1_img2_Im1.jpg", "p3_page1_img3_Im2.png",
    "p4_page1_img2_Im1.jpg", "p4_page2_img2_Im1.jpg",
    "p4_page3_img2_Im1.jpg", "p4_page4_img2_Im1.jpg",
    "p6_page1_img2_Im1.png", "p7_page2_img2_Im1.jpg"
]

for p in photos:
    fpath = os.path.join("fcc_photos", p)
    if os.path.exists(fpath):
        im = Image.open(fpath)
        print(f"{p}: size={im.size}")
