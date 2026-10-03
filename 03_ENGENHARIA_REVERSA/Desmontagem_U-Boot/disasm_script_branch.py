import capstone
with open(r"H:\FEITOS COM IA\Acer-Predator-Connect-T7\2 - Backups Originais de Fabrica\appsbl.bin", "rb") as f:
    elf = f.read()

md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
file_off = 0x5c500
va = file_off - 0x12000 + 0x4a400000
for insn in md.disasm(elf[file_off:file_off+0x80], va):
    print(f"0x{insn.address:08x}:\t{insn.mnemonic}\t{insn.op_str}")
