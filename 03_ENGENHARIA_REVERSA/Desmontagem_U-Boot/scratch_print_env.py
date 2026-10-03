with open(r'Backups_MTD\backup_predator_t7_uboot_env.bin', 'rb') as f:
    env_data = f.read()

# U-Boot env format: CRC (4 bytes) + flags (1 byte if redundant) + string1\0string2\0...\0\0
entries = env_data[4:].split(b'\x00')
for e in entries:
    if e:
        print(e.decode('latin1', errors='replace'))
