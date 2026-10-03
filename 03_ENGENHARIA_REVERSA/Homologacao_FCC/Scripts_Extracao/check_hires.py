from PIL import Image

for name in ["p3_page1_img3_Im2.png", "p6_page1_img2_Im1.png"]:
    im = Image.open(f"fcc_photos/{name}")
    print(f"=== {name} ===")
    print(f"Size: {im.size}, Mode: {im.mode}")
