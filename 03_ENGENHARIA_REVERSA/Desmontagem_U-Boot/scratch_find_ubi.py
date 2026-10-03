with open('appsbl_extracted.bin', 'rb') as f:
    data = f.read()

import struct

# Search for "ubi part" or "do_ubi"
pos = 0
while True:
    idx = data.find(b"ubi part", pos)
    if idx == -1: break
    print(f'"ubi part" found at offset {hex(idx)} (VA {hex(0x4a400000 + idx)})')
    pos = idx + 1
