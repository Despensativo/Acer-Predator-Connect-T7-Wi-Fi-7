import struct

with open(r'\\wsl.localhost\Ubuntu\home\builder\appsbl.bin', 'rb') as f:
    elf = f.read()

# Let's search for ';' (0x3b) comparisons in the code around 0x4a41a000 to 0x4a41b500
code = elf[0x12000:]
for i in range(len(code)-2):
    # cmp rX, #59 (0x3b is ASCII ';') -> 2b3b in Thumb (cmp r3, #59)
    hw = code[i] | (code[i+1] << 8)
    if (hw & 0xff00) == 0x2b00 and (hw & 0xff) == 0x3b:
        reg = (hw >> 8) & 7
        print(f'cmp r{reg}, #59 (";") at vaddr 0x{0x4a400000 + i:x}')
    # cmp.w rX, #59 -> f1bX 0f3b
    if i+3 < len(code):
        hw1 = code[i] | (code[i+1] << 8)
        hw2 = code[i+2] | (code[i+3] << 8)
        if (hw1 & 0xfff0) == 0xf1b0 and hw2 == 0x0f3b:
            reg = hw1 & 0xf
            print(f'cmp.w r{reg}, #59 (";") at vaddr 0x{0x4a400000 + i:x}')
