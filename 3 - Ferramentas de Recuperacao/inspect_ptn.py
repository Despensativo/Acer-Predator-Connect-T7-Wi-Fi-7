import struct

with open(r'\\wsl.localhost\Ubuntu\home\builder\appsbl.bin', 'rb') as f:
    f.seek(0x12000 + (0x4a403b08 - 0x4a400000))
    words = [struct.unpack('<I', f.read(4))[0] for _ in range(40)]
    for i, w in enumerate(words):
        addr = 0x4a403b08 + i * 4
        s = ''
        if 0x4a400000 <= w < 0x4a478000:
            pos = f.tell()
            f.seek(0x12000 + (w - 0x4a400000))
            raw = f.read(32).split(b'\x00')[0]
            f.seek(pos)
            s = f' -> {raw}'
        print(f'{hex(addr)}: {hex(w)}{s}')
