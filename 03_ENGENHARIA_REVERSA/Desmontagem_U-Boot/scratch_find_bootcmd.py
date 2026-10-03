with open('appsbl_extracted.bin', 'rb') as f:
    data = f.read()

import struct

pos = 0
while True:
    idx = data.find(b"bootcmd\x00", pos)
    if idx == -1: break
    va = 0x4a400000 + idx
    print(f'"bootcmd" at {hex(va)}')
    ptr = struct.pack('<I', va)
    p_pos = 0
    while True:
        p_idx = data.find(ptr, p_pos)
        if p_idx == -1: break
        print(f'  Referenced at {hex(0x4a400000 + p_idx)}')
        p_pos = p_idx + 1
    pos = idx + 1
