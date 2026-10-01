import struct

with open(r'\\wsl.localhost\Ubuntu\home\builder\appsbl.bin', 'rb') as f:
    f.seek(0x520d0)
    hdr = f.read(8)
    totalsize = struct.unpack('>I', hdr[4:8])[0]
    f.seek(0x520d0)
    dtb = f.read(totalsize)

with open(r'\\wsl.localhost\Ubuntu\home\builder\uboot.dtb', 'wb') as out:
    out.write(dtb)

print(f'U-Boot DTB extracted: {totalsize} bytes')
