import pypdf
import sys
sys.stdout.reconfigure(encoding="utf-8")

reader = pypdf.PdfReader("FCC_HLZT7_Docs/test_report_2g.pdf")
print("Total pages:", len(reader.pages))
for p in range(min(12, len(reader.pages))):
    txt = reader.pages[p].extract_text()
    for l in txt.split("\n"):
        if any(w in l.lower() for w in ["equipment", "model", "brand", "chip", "qualcomm", "ipq", "qcn", "be11000", "predator", "connect t7", "t7"]):
            print(f"[P{p+1}] {l}")
