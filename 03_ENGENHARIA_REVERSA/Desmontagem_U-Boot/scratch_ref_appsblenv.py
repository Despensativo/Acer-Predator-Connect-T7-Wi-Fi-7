with open('appsbl_extracted.bin', 'rb') as f:
    data = f.read()

import struct

for va in [0x4a450ff1, 0x4a450fef]:
    ptr = struct.pack('<I', va)
    pos = 0
    while True:
        idx = data.find(ptr, pos)
        if idx == -1: break
        print(f"Reference to {hex(va)} at {hex(0x4a400000 + idx)}")
        pos = idx + 1
