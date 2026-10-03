with open('appsbl_extracted.bin', 'rb') as f:
    data = f.read()

import capstone
md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)

# search for calls to 0x4a401348
target_va = 0x4a401348
for off in range(0, len(data)-4, 2):
    va = 0x4a400000 + off
    code = data[off:off+4]
    for insn in md.disasm(code, va):
        if insn.mnemonic in ['bl', 'b'] and hex(target_va) in insn.op_str:
            print(f'Call at {hex(insn.address)}: {insn.mnemonic} {insn.op_str}')
