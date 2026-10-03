with open('appsbl_extracted.bin', 'rb') as f:
    data = f.read()

import capstone
md_thumb = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)

target = 0x4a41aae0
file_off = target - 0x4a400000
for insn in md_thumb.disasm(data[file_off:file_off+0x40], target):
    print(f'0x{insn.address:08x}:\t{insn.mnemonic}\t{insn.op_str}')
