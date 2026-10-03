import pypdf
import sys
sys.stdout.reconfigure(encoding="utf-8")

reader = pypdf.PdfReader("FCC_HLZT7_Docs/user_manual.pdf")
print("Total pages in user manual:", len(reader.pages))
for i, page in enumerate(reader.pages):
    txt = page.extract_text()
    if txt.strip():
        print(f"--- Page {i+1} ---")
        print(txt[:1000])
