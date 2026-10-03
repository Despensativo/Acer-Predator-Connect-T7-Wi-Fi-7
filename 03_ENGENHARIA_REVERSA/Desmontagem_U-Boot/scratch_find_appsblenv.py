with open('appsbl_extracted.bin', 'rb') as f:
    data = f.read()

import struct

for s in [b"APPSBLENV", b"0:APPSBLENV"]:
    pos = 0
    while True:
        idx = data.find(s, pos)
        if idx == -1: break
        print(f"Found {s} at offset {hex(idx)} (VA {hex(0x4a400000 + idx)})")
        pos = idx + 1
