import struct

with open(r'\\wsl.localhost\Ubuntu\home\builder\appsbl.bin', 'rb') as f:
    for addr in [0x4a40af24, 0x4a40af28, 0x4a40af2c, 0x4a40af30, 0x4a40af34, 0x4a40af38, 0x4a40af4c]:
        f.seek(0x12000 + (addr - 0x4a400000))
        val = struct.unpack('<I', f.read(4))[0]
        s = ''
        if 0x4a400000 <= val < 0x4a478000:
            pos = f.tell()
            f.seek(0x12000 + (val - 0x4a400000))
            raw = f.read(32).split(b'\x00')[0]
            f.seek(pos)
            s = f' -> {raw}'
        print(f'{hex(addr)}: {hex(val)}{s}')
