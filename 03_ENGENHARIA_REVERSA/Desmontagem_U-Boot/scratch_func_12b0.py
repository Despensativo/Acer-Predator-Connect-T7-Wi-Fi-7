with open('appsbl_extracted.bin', 'rb') as f:
    data = f.read()

import capstone
md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)

# Find function containing 0x4a401450
target = 0x4a4012b0
file_off = target - 0x4a400000
for insn in md.disasm(data[file_off:file_off+0x1b0], target):
    print(f'0x{insn.address:08x}:\t{insn.mnemonic}\t{insn.op_str}')
