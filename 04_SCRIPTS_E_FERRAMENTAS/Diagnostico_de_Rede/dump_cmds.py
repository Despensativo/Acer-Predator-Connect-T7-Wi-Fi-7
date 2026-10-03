import struct

with open(r'\\wsl.localhost\Ubuntu\home\builder\appsbl.bin', 'rb') as f:
    entry_size = 24
    start_addr = 0x4a469000
    end_addr = 0x4a46a200

    commands = []
    for addr in range(start_addr, end_addr, entry_size):
        f.seek(0x12000 + (addr - 0x4a400000))
        entry = f.read(entry_size)
        if len(entry) < entry_size:
            break
        name_ptr, maxargs, rep, cmd_ptr, usage_ptr, help_ptr = struct.unpack('<6I', entry)
        if 0x4a400000 <= name_ptr < 0x4a478000:
            f.seek(0x12000 + (name_ptr - 0x4a400000))
            name = f.read(32).split(b'\x00')[0].decode('latin1', errors='ignore')
            usage = ''
            if 0x4a400000 <= usage_ptr < 0x4a478000:
                f.seek(0x12000 + (usage_ptr - 0x4a400000))
                usage = f.read(60).split(b'\x00')[0].decode('latin1', errors='ignore')
            if name and name.isprintable() and len(name) < 20:
                commands.append((name, hex(cmd_ptr), usage))

    for name, cmd, usage in commands:
        print(f'{name:<15} cmd={cmd:<12} {usage}')
