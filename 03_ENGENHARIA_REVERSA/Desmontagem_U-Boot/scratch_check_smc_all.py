with open('appsbl_extracted.bin', 'rb') as f:
    data = f.read()

import capstone
md_thumb = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
md_arm = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_ARM)

print("=== Disasm around 0x4a401a7c ===")
target = 0x4a401a60
file_off = target - 0x4a400000
for insn in md_thumb.disasm(data[file_off:file_off+0x40], target):
    print(f"0x{insn.address:08x}:\t{insn.mnemonic}\t{insn.op_str}")

print("\n=== Disasm around 0x4a400398 ===")
target = 0x4a400388
file_off = target - 0x4a400000
for insn in md_arm.disasm(data[file_off:file_off+0x30], target):
    print(f"0x{insn.address:08x}:\t{insn.mnemonic}\t{insn.op_str}")
