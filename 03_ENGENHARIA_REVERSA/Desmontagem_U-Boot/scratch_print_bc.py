with open(r'Backups_MTD\backup_predator_t7_bootconfig.bin', 'rb') as f:
    orig = f.read()

import struct
print("Count:", struct.unpack('<I', orig[8:12])[0])
for i in range(6):
    base = 12 + i * 20
    name = orig[base:base+16].split(b'\x00')[0]
    val = struct.unpack('<I', orig[base+16:base+20])[0]
    print(f"Entry {i} (offset {hex(base)}): name={name} val={val} (raw={orig[base+16:base+20].hex()})")
