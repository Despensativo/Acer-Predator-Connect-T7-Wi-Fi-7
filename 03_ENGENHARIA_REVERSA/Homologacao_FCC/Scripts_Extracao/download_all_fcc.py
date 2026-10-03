import urllib.request
import os

docs = {
    "internal_photos_part2.pdf": "https://fccid.io/HLZT7/Internal-Photos/9-Internal-Photos-Part2-7455751.pdf",
    "internal_photos_part3.pdf": "https://fccid.io/HLZT7/Internal-Photos/9-Internal-Photos-Part3-7455752.pdf",
    "internal_photos_part4.pdf": "https://fccid.io/HLZT7/Internal-Photos/9-Internal-Photos-Part4-7455753.pdf",
    "internal_photos_part5.pdf": "https://fccid.io/HLZT7/Internal-Photos/9-Internal-Photos-Part5-7455754.pdf",
    "internal_photos_part6.pdf": "https://fccid.io/HLZT7/Internal-Photos/9-Internal-Photos-Part6-7455755.pdf",
    "internal_photos_part7.pdf": "https://fccid.io/HLZT7/Internal-Photos/9-Internal-Photos-Part7-7455756.pdf",
    "antenna_spec.pdf": "https://fccid.io/HLZT7/Test-Report/Antenna-Spec-7449370.pdf",
    "attestation_wifi6e_7.pdf": "https://fccid.io/HLZT7/Attestation-Statements/WIFI-6E-7-AttestationLetter-7455747.pdf",
    "user_manual.pdf": "https://fccid.io/HLZT7/User-Manual/8-UserManual-7455749.pdf",
    "test_report_2g.pdf": "https://fccid.io/HLZT7/Test-Report/BTL-FCCP-1-2311H013-R01-WLAN2-4G-1-7449471.pdf",
    "test_report_5g.pdf": "https://fccid.io/HLZT7/Test-Report/BTL-FCCP-2-2311H013-R02-RLAN1-4-1-7449507.pdf",
    "test_report_6g.pdf": "https://fccid.io/HLZT7/Test-Report/BTL-FCCP-4-2311H013-R02-UNLL5-8-1-7449468.pdf",
    "rf_exposure_mpe.pdf": "https://fccid.io/HLZT7/RF-Exposure-Info/Test-Report-BTL-FCCP-5-2311H013-MPE-R01-7449371.pdf"
}

os.makedirs("FCC_HLZT7_Docs", exist_ok=True)
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

for fname, url in docs.items():
    dst = os.path.join("FCC_HLZT7_Docs", fname)
    if os.path.exists(dst) and os.path.getsize(dst) > 1000:
        print(f"Already exists: {fname}")
        continue
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = resp.read()
            with open(dst, "wb") as f:
                f.write(data)
            print(f"Downloaded: {fname} ({len(data)} bytes)")
    except Exception as e:
        print(f"Failed {fname}: {e}")
