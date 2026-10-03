import struct

with open(r'\\wsl.localhost\Ubuntu\home\builder\appsbl.bin', 'rb') as f:
    elf = f.read()

idx = elf.find(b'board_eth_init\x00')
print(f'board_eth_init string at 0x{idx:x}')

# Find references to board_eth_init or board_init
pos = 0
vaddr = 0x4a400000 + (idx - 0x12000)
target = struct.pack('<I', vaddr)
while True:
    ref = elf.find(target, pos)
    if ref == -1:
        break
    print(f'Reference at 0x{ref:x} (vaddr 0x{0x4a400000 + ref - 0x12000:x})')
    pos = ref + 1
