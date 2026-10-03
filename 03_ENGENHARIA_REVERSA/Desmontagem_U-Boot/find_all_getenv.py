import capstone, struct

with open('appsbl_extracted.bin', 'rb') as f:
    data = f.read()

md_thumb = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)

calls = []
# BL target in thumb: 4-byte instruction starting with 0xf0-0xf7
for off in range(0, len(data)-4, 2):
    insns = list(md_thumb.disasm(data[off:off+4], 0x4a400000 + off))
    if insns:
        insn = insns[0]
        if insn.mnemonic == 'bl' and '#0x4a417830' in insn.op_str:
            calls.append(insn.address)

print(f'Total getenv calls: {len(calls)}')

def get_str(addr):
    off = addr - 0x4a400000
    if 0 <= off < len(data):
        end = data.find(b'\x00', off)
        if end != -1 and end - off < 60:
            return data[off:end].decode('ascii', errors='ignore')
    return ''

for addr in calls:
    off = addr - 0x4a400000
    found_var = None
    for delta in range(2, 40, 2):
        p_addr = addr - delta
        p_off = p_addr - 0x4a400000
        p_insns = list(md_thumb.disasm(data[p_off:p_off+4], p_addr))
        if p_insns and p_insns[0].mnemonic == 'ldr' and p_insns[0].op_str.startswith('r0, [pc'):
            op = p_insns[0].op_str
            try:
                hex_off = int(op.split('#')[1].rstrip(']'), 16)
                pc_val = (p_addr + 4) & ~3
                lit_addr = pc_val + hex_off
                lit_val = struct.unpack('<I', data[lit_addr - 0x4a400000 : lit_addr - 0x4a400000 + 4])[0]
                s = get_str(lit_val)
                if s:
                    found_var = s
                    break
            except Exception as e:
                pass
    if found_var:
        print(f'0x{addr:08x}: getenv("{found_var}")')
    else:
        print(f'0x{addr:08x}: getenv(?)')
