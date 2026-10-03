with open('appsbl_extracted.bin', 'rb') as f:
    data = f.read()

import struct

val = struct.unpack('<I', data[0x4a406ae0-0x4a400000:0x4a406ae4-0x4a400000])[0]
print("ptr:", hex(val))
if 0x4a400000 <= val < 0x4a400000 + len(data):
    print("str:", data[val-0x4a400000:val-0x4a400000+64])
