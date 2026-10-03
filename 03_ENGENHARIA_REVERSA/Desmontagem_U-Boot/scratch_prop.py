with open('appsbl_extracted.bin', 'rb') as f:
    data = f.read()

import struct

for va in range(0x4a4038f0, 0x4a403910, 4):
    off = va - 0x4a400000
    val = struct.unpack('<I', data[off:off+4])[0]
    print(hex(va), hex(val))
    if 0x4a400000 <= val < 0x4a400000 + len(data):
        print("  ->", data[val-0x4a400000:val-0x4a400000+32])
