with open('appsbl_extracted.bin', 'rb') as f:
    data = f.read()

import struct

def get_str(va):
    if 0x4a400000 <= va < 0x4a400000 + len(data):
        off = va - 0x4a400000
        return data[off:off+128].split(b'\x00')[0]
    return b''

# In func_2a68:
# 0x4a402b7e: ldr r2, [pc, #0x14c] -> pc is 0x4a402b82, + 0x14c = 0x4a402cce
# let's check what is at 0x4a402ccc:
val = struct.unpack('<I', data[0x4a402ccc-0x4a400000:0x4a402cd0-0x4a400000])[0]
print("0x4a402ccc ptr:", hex(val), get_str(val))

# What is at 0x4a402cc0:
val = struct.unpack('<I', data[0x4a402cc0-0x4a400000:0x4a402cc4-0x4a400000])[0]
print("0x4a402cc0 ptr:", hex(val), get_str(val))
