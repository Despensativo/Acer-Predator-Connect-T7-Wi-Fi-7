import capstone
with open(r"H:\FEITOS COM IA\Acer-Predator-Connect-T7\2 - Backups Originais de Fabrica\appsbl.bin", "rb") as f:
    elf = f.read()

md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
target_va = 0x4a465e0c
start_va = target_va - 250
file_start = start_va - 0x4a400000 + 0x12000
for insn in md.disasm(elf[file_start:file_start+250], start_va):
    print(f"0x{insn.address:08x}:\t{insn.mnemonic}\t{insn.op_str}")
