with open(r"H:\FEITOS COM IA\Acer-Predator-Connect-T7\2 - Backups Originais de Fabrica\appsbl.bin", "rb") as f:
    elf = f.read()

pos = elf.find(b"\nStarting kernel")
va = pos - 0x12000 + 0x4a400000
print("Starting kernel va:", hex(va))

# Let us search for occurrences of the low 16 bits or references
import struct
for off in range(0x12000, 0x50000, 2):
    # check if thumb literal or adr
    pass

# Let us find xref by looking for the pointer in any literal pool
needle = struct.pack("<I", va)
for off in range(0, len(elf)-4, 4):
    if elf[off:off+4] == needle:
        print("Literal xref at:", hex(off), "va:", hex(off - 0x12000 + 0x4a400000))
