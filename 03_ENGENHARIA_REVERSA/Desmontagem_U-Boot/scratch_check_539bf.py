with open('appsbl_extracted.bin', 'rb') as f:
    data = f.read()

off = 0x539bf
print("String around 0x539bf:", data[off-32:off+64])

import struct
val = struct.pack('<I', 0x4a400000 + off)
pos = 0
while True:
    idx = data.find(val, pos)
    if idx == -1: break
    print("Referenced at:", hex(0x4a400000 + idx))
    pos = idx + 1
