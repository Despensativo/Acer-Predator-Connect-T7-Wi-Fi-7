import pypdf
import sys
sys.stdout.reconfigure(encoding="utf-8")

reader = pypdf.PdfReader("FCC_HLZT7_Docs/test_report_5g.pdf")
for p in range(11, 25):
    txt = reader.pages[p].extract_text()
    if any(k in txt.lower() for k in ["description of eut", "antenna", "transceiver", "qualcomm", "ipq", "qcn", "qca"]):
        print(f"=== Page {p+1} ===")
        print(txt[:1000])
