import os
import pypdf
import re

docs_dir = "FCC_HLZT7_Docs"
results = {}

keywords = [
    "IPQ", "QCN", "QCA", "FEM", "Skyworks", "Qorvo", "Richwave",
    "DDR", "NAND", "Flash", "PHY", "Switch", "Antenna",
    "2.4G", "5G", "6G", "320MHz", "160MHz", "4096", "MLO",
    "Memory", "Ethernet", "W25N", "Winbond", "Macronix", "MXIC",
    "Micron", "Samsung", "Nanya", "SK Hynix", "Aquantia", "Atheros"
]

for fname in sorted(os.listdir(docs_dir)):
    if not fname.endswith(".pdf"):
        continue
    fpath = os.path.join(docs_dir, fname)
    print(f"--- Scanning {fname} ---")
    try:
        reader = pypdf.PdfReader(fpath)
        full_text = ""
        for i, page in enumerate(reader.pages):
            txt = page.extract_text() or ""
            full_text += f"\n[P{i+1}] " + txt
        
        found = {}
        for kw in keywords:
            matches = re.findall(rf'([^\n.]{{0,40}}{kw}[^\n.]{{0,40}})', full_text, re.IGNORECASE)
            if matches:
                # Deduplicate and limit to 3 examples
                clean = list(set([m.strip() for m in matches]))[:3]
                found[kw] = clean
        
        if found:
            print(f"  Keywords in {fname}: {list(found.keys())}")
            results[fname] = found
    except Exception as e:
        print(f"  Error reading {fname}: {e}")

# Save results
import json
with open("fcc_extracted_keywords.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print("Saved fcc_extracted_keywords.json")
