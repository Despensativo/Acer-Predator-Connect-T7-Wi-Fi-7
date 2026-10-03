with open(r'Backups_MTD\backup_predator_t7_bootconfig.bin', 'rb') as f:
    orig = f.read()

with open(r'Backups_MTD\bootconfig_slot2_openwrt.bin', 'rb') as f:
    slot2 = f.read()

diffs = []
for i in range(len(orig)):
    if orig[i] != slot2[i]:
        diffs.append((hex(i), hex(orig[i]), hex(slot2[i])))

print(f"Total diffs: {len(diffs)}")
for d in diffs[:20]:
    print(d)

print("\nDump of first 0x100 bytes of orig:")
import binascii
print(binascii.hexlify(orig[:0x100]))
