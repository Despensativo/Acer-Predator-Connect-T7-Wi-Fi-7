import os
import struct

path = r'Backups_MTD\nand-4k-ipq5332-single_101000024.img'
size = os.path.getsize(path)
print(f"File: {path}, Size: {size} bytes")

with open(path, 'rb') as f:
    hdr = f.read(128)

print("Header hex:", hdr[:32].hex())
magic = struct.unpack('>I', hdr[:4])[0]
print(f"Magic: 0x{magic:08x}")
if magic == 0xd00dfeed:
    print("IT IS A VALID STANDARD FDT / FIT IMAGE!")
    totalsize = struct.unpack('>I', hdr[4:8])[0]
    print(f"FIT declared total size: {totalsize} bytes")
else:
    print("Not standard FIT magic")

with open(path, 'rb') as f:
    full = f.read()

keywords = [b'ubi', b'kernel', b'rootfs', b'mibib', b'sbl1', b'tz', b'rpm', b'u-boot', b'ddr', b'squashfs', b'hsqs']
print("\nSearching keywords in image:")
for k in keywords:
    c = full.count(k)
    pos = full.find(k)
    name = k.decode('ascii')
    print(f"  {name}: {c} occurrences, first at 0x{pos:x}")
