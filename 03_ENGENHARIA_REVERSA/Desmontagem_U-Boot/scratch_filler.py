with open('appsbl_extracted.bin', 'rb') as f:
    data = f.read()

import capstone
md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)

for target in [0x4a400c20, 0x4a401460, 0x4a401580]:
    print(f'=== Target {hex(target)} ===')
    file_off = target - 0x4a400000
    for insn in md.disasm(data[file_off:file_off+0x60], target):
        print(f'0x{insn.address:08x}:\t{insn.mnemonic}\t{insn.op_str}')
