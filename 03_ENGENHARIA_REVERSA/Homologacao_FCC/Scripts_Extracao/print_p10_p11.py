import pypdf
import sys
sys.stdout.reconfigure(encoding="utf-8")

reader = pypdf.PdfReader("FCC_HLZT7_Docs/test_report_2g.pdf")
print("=== PAGE 10 ===")
print(reader.pages[9].extract_text())
print("=== PAGE 11 ===")
print(reader.pages[10].extract_text())
