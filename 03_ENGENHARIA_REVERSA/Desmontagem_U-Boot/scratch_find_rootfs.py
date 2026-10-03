with open('appsbl_extracted.bin', 'rb') as f:
    data = f.read()

import struct

for s in [b"rootfs_1\x00", b"rootfs\x00"]:
    pos = 0
    while True:
        idx = data.find(s, pos)
        if idx == -1: break
        va = 0x4a400000 + idx
        print(f"String {s} at VA {hex(va)}")
        # find pointers to va
        ptr = struct.pack('<I', va)
        p_pos = 0
        while True:
            p_idx = data.find(ptr, p_pos)
            if p_idx == -1: break
            print(f"  Referenced at VA {hex(0x4a400000 + p_idx)}")
            p_pos = p_idx + 1
        pos = idx + 1
