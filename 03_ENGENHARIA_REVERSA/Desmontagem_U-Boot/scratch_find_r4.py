with open('appsbl_extracted.bin', 'rb') as f:
    data = f.read()

import struct

# 0x4a402aa6: pc is 0x4a402aaa. 0x4a402aaa + 0x20c = 0x4a402cb6 -> 0x4a402cb4
val = struct.unpack('<I', data[0x4a402cb4-0x4a400000:0x4a402cb8-0x4a400000])[0]
print("0x4a402cb4 val:", hex(val))

# Let's inspect where val is initialized
print("Searching references to pointer:", hex(val))
ptr_bytes = struct.pack('<I', val)
pos = 0
while True:
    idx = data.find(ptr_bytes, pos)
    if idx == -1: break
    print(f'Reference to {hex(val)} at {hex(0x4a400000 + idx)}')
    pos = idx + 1
