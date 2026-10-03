with open('appsbl_extracted.bin', 'rb') as f:
    data = f.read()

import struct

def dump_ptr(va):
    off = va - 0x4a400000
    val = struct.unpack('<I', data[off:off+4])[0]
    s = b""
    if 0x4a400000 <= val < 0x4a400000 + len(data):
        s = data[val-0x4a400000:val-0x4a400000+64].split(b'\x00')[0]
    print(f"{hex(va)}: ptr={hex(val)} -> {s}")

# At 0x4a4027a0: ldr r1, [pc, #0x15c] -> pc is 0x4a4027a4 -> 0x4a4027a4 + 0x15c = 0x4a402900
dump_ptr(0x4a402900)

# At 0x4a4027f2: ldr r1, [pc, #0x118] -> pc is 0x4a4027f6 -> 0x4a4027f6 + 0x118 = 0x4a40290e -> 0x4a40290c
dump_ptr(0x4a40290c)

# At 0x4a40280a: ldr r1, [pc, #0xd4] -> pc is 0x4a40280e -> 0x4a40280e + 0xd4 = 0x4a4028e2 -> 0x4a4028e0
dump_ptr(0x4a4028e0)
