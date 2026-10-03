with open('appsbl_extracted.bin', 'rb') as f:
    data = f.read()

import struct

# Let's find "bootm\x00"
pos = 0
while True:
    idx = data.find(b'bootm\x00', pos)
    if idx == -1: break
    va = 0x4a400000 + idx
    print(f'"bootm" at {hex(va)}')
    # find cmd_tbl entry
    ptr = struct.pack('<I', va)
    p_pos = 0
    while True:
        p_idx = data.find(ptr, p_pos)
        if p_idx == -1: break
        print(f'  Referenced at {hex(0x4a400000 + p_idx)}')
        p_pos = p_idx + 1
    pos = idx + 1
