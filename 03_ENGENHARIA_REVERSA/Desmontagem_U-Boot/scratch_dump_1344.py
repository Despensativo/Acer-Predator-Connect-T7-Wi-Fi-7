with open('appsbl_extracted.bin', 'rb') as f:
    data = f.read()

import struct

for va in range(0x4a401344, 0x4a401390, 4):
    off = va - 0x4a400000
    val = struct.unpack('<I', data[off:off+4])[0]
    print(hex(va), hex(val))
