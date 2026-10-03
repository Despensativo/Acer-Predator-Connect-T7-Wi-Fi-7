import pypdf
import sys
sys.stdout.reconfigure(encoding="utf-8")

reader = pypdf.PdfReader("FCC_HLZT7_Docs/user_manual.pdf")
for i in range(min(10, len(reader.pages))):
    print(f"--- Page {i+1} ---")
    print(reader.pages[i].extract_text())
