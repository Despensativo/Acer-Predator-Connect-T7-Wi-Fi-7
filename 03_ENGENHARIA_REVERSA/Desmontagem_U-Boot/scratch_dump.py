import struct

with open('appsbl_extracted.bin', 'rb') as f:
    data = f.read()

def dump_strings(start_va, end_va):
    for va in range(start_va, end_va, 4):
        off = va - 0x4a400000
        val = struct.unpack('<I', data[off:off+4])[0]
        if 0x4a400000 <= val < 0x4a400000 + len(data):
            str_off = val - 0x4a400000
            s = data[str_off:str_off+64].split(b'\x00')[0]
            try:
                s_txt = s.decode('ascii')
                print(f'{hex(va)}: -> {hex(val)}: "{s_txt}"')
            except:
                print(f'{hex(va)}: -> {hex(val)}: {s}')
        else:
            print(f'{hex(va)}: {hex(val)}')

print('=== Literals for func_26d0 ===')
dump_strings(0x4a402870, 0x4a402920)
