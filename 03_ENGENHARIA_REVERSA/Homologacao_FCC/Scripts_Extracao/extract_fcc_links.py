with open("fcc_hlzt7.html", encoding="utf-8") as f:
    c = f.read()

import re
matches = re.findall(r'href="([^"]+)"', c)
for m in matches:
    if any(k in m for k in ["pdf", "eas", "oet", "7455", "7449"]):
        print(m)
