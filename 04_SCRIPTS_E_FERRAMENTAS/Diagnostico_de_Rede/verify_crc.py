import zlib, struct

# Dump directly over SSH using python or read from WSL
import subprocess
out = subprocess.check_output([
    'wsl', '-u', 'builder', 'bash', '-c',
    'sshpass -p admin0100 ssh -o StrictHostKeyChecking=no -o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedKeyTypes=+ssh-rsa root@192.168.73.2 "cat /dev/mtd13"'
])

stored_crc = struct.unpack('<I', out[:4])[0]
computed_crc = zlib.crc32(out[4:0x40000]) & 0xffffffff
print(f'Stored CRC:   0x{stored_crc:08x}')
print(f'Computed CRC: 0x{computed_crc:08x}')
if stored_crc == computed_crc:
    print('CRC IS 100% VALID!')
else:
    print('MISMATCH!')
