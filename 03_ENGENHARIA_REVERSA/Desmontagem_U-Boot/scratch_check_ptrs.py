with open('appsbl_extracted.bin', 'rb') as f:
    data = f.read()

import struct

# 0x4a4027d6: pc is 0x4a4027da -> 0x4a4027da + 0x130 = 0x4a40290a -> 0x4a402908
val = struct.unpack('<I', data[0x4a402908-0x4a400000:0x4a40290c-0x4a400000])[0]
print("0x4a402908 ptr:", hex(val), data[val-0x4a400000:val-0x4a400000+32])

# Also check 0x4a4027b4 and 0x4a4027bc
val_bc = struct.unpack('<I', data[0x4a4028ec-0x4a400000:0x4a4028f0-0x4a400000])[0]
print("0x4a4028ec ptr:", hex(val_bc), data[val_bc-0x4a400000:val_bc-0x4a400000+32])
