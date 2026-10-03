import pypdf
import sys
sys.stdout.reconfigure(encoding="utf-8")

reader = pypdf.PdfReader("FCC_HLZT7_Docs/attestation_wifi6e_7.pdf")
for i, p in enumerate(reader.pages):
    print(f"--- Page {i+1} ---")
    print(p.extract_text())
