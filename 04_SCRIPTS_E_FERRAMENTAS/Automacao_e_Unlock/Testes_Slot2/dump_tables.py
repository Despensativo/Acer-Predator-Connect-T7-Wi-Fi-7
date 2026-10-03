import struct
with open(r"H:\FEITOS COM IA\Acer-Predator-Connect-T7\2 - Backups Originais de Fabrica\appsbl.bin", "rb") as f:
    elf = f.read()

def get_str(va):
    off = va - 0x4a400000 + 0x12000
    if 0 <= off < len(elf):
        end = elf.find(b"\x00", off)
        return elf[off:end].decode("latin1")
    return ""

base_va = 0x4a44eac0
for i in range(25):
    va = base_va + i*12
    foff = va - 0x4a400000 + 0x12000
    id_val, name_ptr, lname_ptr = struct.unpack("<III", elf[foff:foff+12])
    print(f"Entry {i}: id={id_val} name=\"{get_str(name_ptr)}\" lname=\"{get_str(lname_ptr)}\"")
