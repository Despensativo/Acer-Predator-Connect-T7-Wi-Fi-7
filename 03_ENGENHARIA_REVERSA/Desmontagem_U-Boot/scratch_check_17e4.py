with open('appsbl_extracted.bin', 'rb') as f:
    data = f.read()

import struct

for va in range(0x4a4017d0, 0x4a401820, 4):
    off = va - 0x4a400000
    val = struct.unpack('<I', data[off:off+4])[0]
    s = ""
    if 0x4a400000 <= val < 0x4a400000 + len(data):
        s = data[val-0x4a400000:val-0x4a400000+64].split(b'\x00')[0]
    print(hex(va), hex(val), s)
