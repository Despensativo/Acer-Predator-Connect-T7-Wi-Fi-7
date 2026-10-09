import pypdf
import re
import sys
sys.stdout.reconfigure(encoding="utf-8")

def parse_eut_info(pdf_path):
    print(f"\n==========================================")
    print(f"FILE: {pdf_path}")
    print(f"==========================================")
    reader = pypdf.PdfReader(pdf_path)
    for p_idx in range(min(15, len(reader.pages))):
        text = reader.pages[p_idx].extract_text()
        for heading in ["1. GENERAL INFORMATION", "1.1 DESCRIPTION OF EUT", "1.2 TABLE FOR FILED ANTENNA", "EUT Specification", "Antenna Specification", "Operational Description"]:
            if heading.lower() in text.lower():
                print(f"\n--- Found '{heading}' on Page {p_idx+1} ---")
                # Print relevant 1000 characters
                pos = text.lower().find(heading.lower())
                print(text[pos:pos+1500])

parse_eut_info("FCC_HLZT7_Docs/test_report_2g.pdf")
parse_eut_info("FCC_HLZT7_Docs/antenna_spec.pdf")
parse_eut_info("FCC_HLZT7_Docs/attestation_wifi6e_7.pdf")
