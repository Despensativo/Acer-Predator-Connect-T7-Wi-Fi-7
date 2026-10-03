import pypdf

reader = pypdf.PdfReader("internal_photos_part1.pdf")
print("Num pages:", len(reader.pages))
for i, page in enumerate(reader.pages):
    txt = page.extract_text()
    if txt.strip():
        print(f"--- Page {i+1} ---")
        print(txt[:400])
