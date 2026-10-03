with open(r"H:\FEITOS COM IA\Acer-Predator-Connect-T7\2 - Backups Originais de Fabrica\appsbl.bin", "rb") as f:
    elf = f.read()

pos = elf.find(b"unsupported partition name")
va = pos - 0x12000 + 0x4a400000
print("String va:", hex(va))

import struct
needle = struct.pack("<I", va)
for off in range(0, len(elf)-4, 4):
    if elf[off:off+4] == needle:
        print("Literal xref at:", hex(off), "va:", hex(off - 0x12000 + 0x4a400000))
