import pypdf
import sys
sys.stdout.reconfigure(encoding="utf-8")

for name in ["test_report_5g.pdf", "test_report_6g.pdf"]:
    print(f"\n=================== {name} ===================")
    reader = pypdf.PdfReader(f"FCC_HLZT7_Docs/{name}")
    print(reader.pages[9].extract_text())
    print(reader.pages[10].extract_text())
