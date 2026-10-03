import struct
with open(r"H:\FEITOS COM IA\Acer-Predator-Connect-T7\Backups_MTD\backup_predator_t7_mibib.bin", "rb") as f:
    data = f.read()

# Qualcomm partition table header:
# magic1: 0x55ee73aa, magic2: 0xe35ebddb, version: 4, numparts: uint32
for off in range(0, len(data)-32, 4):
    m1, m2 = struct.unpack("<II", data[off:off+8])
    if m1 == 0x55ee73aa and m2 == 0xe35ebddb:
        ver, numparts = struct.unpack("<II", data[off+8:off+16])
        print(f"MIBIB at {hex(off)}: ver={ver}, numparts={numparts}")
        # Each partition entry is 28 bytes in v4
        p_off = off + 16
        for p in range(numparts):
            pdata = data[p_off + p*28 : p_off + (p+1)*28]
            name = pdata[:16].rstrip(b"\x00").decode("latin1")
            offset_blks, size_blks = struct.unpack("<II", pdata[16:24])
            # block size is 256KB = 0x40000
            start_addr = offset_blks * 0x40000
            size_bytes = size_blks * 0x40000
            print(f"  {p:2d}: {name:<16} blk {offset_blks:#06x} ({start_addr:#010x}) len {size_blks:#06x} ({size_bytes/(1024*1024):.1f} MB)")
        break
