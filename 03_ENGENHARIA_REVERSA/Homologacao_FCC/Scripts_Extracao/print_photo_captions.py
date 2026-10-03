import pypdf
import os
import sys
sys.stdout.reconfigure(encoding="utf-8")

docs_dir = "FCC_HLZT7_Docs"
for f in sorted(os.listdir(docs_dir)):
    if f.startswith("internal_photos"):
        reader = pypdf.PdfReader(os.path.join(docs_dir, f))
        print(f"\n=== {f} ({len(reader.pages)} pages) ===")
        for p_idx, page in enumerate(reader.pages):
            txt = page.extract_text() or ""
            lines = [l.strip() for l in txt.split("\n") if l.strip()]
            print(f"  Page {p_idx+1}: {lines}")
