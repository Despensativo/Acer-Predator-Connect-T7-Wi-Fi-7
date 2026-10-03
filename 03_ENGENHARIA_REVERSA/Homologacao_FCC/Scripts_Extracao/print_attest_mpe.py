import pypdf
import sys
sys.stdout.reconfigure(encoding="utf-8")

def print_full(fname):
    print(f"\n=================== {fname} ===================")
    reader = pypdf.PdfReader(f"FCC_HLZT7_Docs/{fname}")
    for i, p in enumerate(reader.pages):
        print(f"--- Page {i+1} ---")
        print(p.extract_text())

print_full("attestation_wifi6e_7.pdf")
print_full("rf_exposure_mpe.pdf")
