with open('appsbl_extracted.bin', 'rb') as f:
    data = f.read()

import struct

for va in range(0x4a45ea20, 0x4a45ea90):
    val = struct.pack('<I', va)
    pos = 0
    while True:
        idx = data.find(val, pos)
        if idx == -1: break
        print(f"Reference to {hex(va)} ({data[va-0x4a400000:va-0x4a400000+25]}) at {hex(0x4a400000 + idx)}")
        pos = idx + 1
