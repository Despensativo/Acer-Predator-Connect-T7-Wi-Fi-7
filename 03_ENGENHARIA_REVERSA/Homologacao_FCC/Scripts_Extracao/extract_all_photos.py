import pypdf
import os

docs_dir = "FCC_HLZT7_Docs"
os.makedirs("fcc_photos", exist_ok=True)

for p_num in range(2, 8):
    fname = f"internal_photos_part{p_num}.pdf"
    fpath = os.path.join(docs_dir, fname)
    if not os.path.exists(fpath):
        continue
    reader = pypdf.PdfReader(fpath)
    print(f"Extracting {fname} ({len(reader.pages)} pages)...")
    for idx, page in enumerate(reader.pages):
        for img_idx, img in enumerate(page.images):
            out_name = f"fcc_photos/p{p_num}_page{idx+1}_img{img_idx+1}_{img.name}"
            # Only save jpg/png > 50KB (actual photos)
            if len(img.data) > 50000:
                with open(out_name, "wb") as f:
                    f.write(img.data)
                print(f"  Saved: {out_name} ({len(img.data)} bytes)")
print("Done extracting all photos!")
