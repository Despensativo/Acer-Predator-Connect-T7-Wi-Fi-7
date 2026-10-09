import struct

with open(r'\\wsl.localhost\Ubuntu\home\builder\appsbl.bin', 'rb') as f:
    elf = f.read()

idx = elf.find(b'bootipq\x00')
print(f'bootipq string at 0x{idx:x}')

# Find command table entry for bootipq
# In U-Boot: struct cmd_tbl_s:
# name, maxargs, repeatable, (*cmd)(cmd_tbl_t *, int, int, char * const []), usage, help, complete
pos = 0
vaddr = 0x4a400000 + (idx - 0x12000)
target = struct.pack('<I', vaddr)
while True:
    ref = elf.find(target, pos)
    if ref == -1:
        break
    print(f'Reference at 0x{ref:x} (vaddr 0x{0x4a400000 + ref - 0x12000:x})')
    pos = ref + 1
