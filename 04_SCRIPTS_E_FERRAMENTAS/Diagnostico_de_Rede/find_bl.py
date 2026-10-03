with open(r'\\wsl.localhost\Ubuntu\home\builder\appsbl.bin', 'rb') as f:
    f.seek(0x12000)
    code = f.read(0x78048)

for i in range(0, len(code)-4, 2):
    hw1 = code[i] | (code[i+1] << 8)
    hw2 = code[i+2] | (code[i+3] << 8)
    if (hw1 & 0xf800) == 0xf000 and (hw2 & 0xd000) == 0xd000: # BL
        s = (hw1 >> 10) & 1
        j1 = (hw2 >> 13) & 1
        j2 = (hw2 >> 11) & 1
        imm10 = hw1 & 0x3ff
        imm11 = hw2 & 0x7ff
        i1 = ~(j1 ^ s) & 1
        i2 = ~(j2 ^ s) & 1
        imm32 = (s << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12) | (imm11 << 1)
        if s:
            imm32 -= (1 << 25)
        pc = 0x4a400000 + i + 4
        dest = pc + imm32
        if (dest & ~1) == 0x4a417ad4:
            print(f'BL from 0x{0x4a400000 + i:x} to 0x{dest:x}')
