import pypdf
import re

for doc in ["test_report_2g.pdf", "test_report_5g.pdf", "test_report_6g.pdf", "rf_exposure_mpe.pdf"]:
    reader = pypdf.PdfReader(f"FCC_HLZT7_Docs/{doc}")
    full = ""
    for p in reader.pages:
        full += p.extract_text() or ""
    
    # search for chip models
    chips = re.findall(r'(IPQ\d+|QCN\d+|QCA\d+|W25N\d+|Skyworks|Qorvo|SE\d+|RTC\d+|MXIC|W97|W63|NT5C)', full, re.IGNORECASE)
    print(f"{doc}: found chips -> {set(chips)}")
