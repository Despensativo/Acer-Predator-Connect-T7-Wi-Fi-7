with open('appsbl_extracted.bin', 'rb') as f:
    data = f.read()

import struct

val = struct.unpack('<I', data[0x4a4038fe-0x4a400000:0x4a403902-0x4a400000])[0]
print("ptr at 0x4a4038fe:", hex(val))

import capstone
md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)

target = 0x4a440210
file_off = target - 0x4a400000
for insn in md.disasm(data[file_off:file_off+0x60], target):
    print(f'0x{insn.address:08x}:\t{insn.mnemonic}\t{insn.op_str}')
