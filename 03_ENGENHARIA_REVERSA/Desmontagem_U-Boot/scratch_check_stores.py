with open('appsbl_extracted.bin', 'rb') as f:
    data = f.read()

import capstone
md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)

for va in [0x4a400c30, 0x4a401470]:
    target = va - 0x20
    file_off = target - 0x4a400000
    print(f"=== Disasm around {hex(va)} ===")
    for insn in md.disasm(data[file_off:file_off+0x50], target):
        print(f'0x{insn.address:08x}:\t{insn.mnemonic}\t{insn.op_str}')
