import pypdf
import os

reader = pypdf.PdfReader("internal_photos_part1.pdf")
os.makedirs("fcc_photos", exist_ok=True)
count = 0
for idx, page in enumerate(reader.pages):
    for img_idx, img in enumerate(page.images):
        fname = f"fcc_photos/p1_page{idx+1}_img{img_idx+1}_{img.name}"
        with open(fname, "wb") as f:
            f.write(img.data)
        print(f"Saved: {fname} ({len(img.data)} bytes)")
        count += 1
print(f"Total extracted: {count}")
