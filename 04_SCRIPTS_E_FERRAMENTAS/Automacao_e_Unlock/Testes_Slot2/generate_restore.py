import os
import subprocess

base_dir = r"/mnt/h/FEITOS COM IA/Acer-Predator-Connect-T7"
tools_dir = f"{base_dir}/3 - Ferramentas de Recuperacao"
mtd_dir = f"{base_dir}/Backups_MTD"

cmd_script = """echo ========================================================
echo RESTAURANDO TUDO DE FABRICA PARA SLOT 1 (ACER 100% ORIGINAL)
echo ========================================================
setenv fsbootargs
setenv bootargs console=ttyMSM0,115200n8
setenv bootcmd bootipq
saveenv
imxtract 0x44000000 bootconfig 0x45000000
mw.b 0x4500006c 0x01
nand device 0
nand erase 0x400000 0x80000
nand write 0x45000000 0x400000 0x80000
nand erase 0x480000 0x80000
nand write 0x45000000 0x480000 0x80000
echo ========================================================
echo REINICIANDO AGORA NO FIRMWARE ORIGINAL DA ACER...
echo ========================================================
reset
"""

with open("/tmp/restore_slot1.scr", "w") as f:
    f.write(cmd_script)

# Copy backup bootconfig
subprocess.run(["cp", f"{mtd_dir}/backup_predator_t7_bootconfig.bin", "/tmp/bootconfig.bin"], check=True)

# Create 32KB padding
with open("/tmp/pad32k.bin", "wb") as f:
    f.write(b"\x00" * 32768)

its_content = """/dts-v1/;

/ {
\tdescription = "Flash Restore Stock";
\t#address-cells = <1>;

\timages {
\t\tscript {
\t\t\tdescription = "Restore Stock Slot 1 Script";
\t\t\tdata = /incbin/("/tmp/restore_slot1.scr");
\t\t\ttype = "script";
\t\t\tcompression = "none";
\t\t\thash-1 {
\t\t\t\talgo = "crc32";
\t\t\t};
\t\t};
\t\tbootconfig {
\t\t\tdescription = "Original Bootconfig Slot 1";
\t\t\tdata = /incbin/("/tmp/bootconfig.bin");
\t\t\ttype = "firmware";
\t\t\tcompression = "none";
\t\t\thash-1 {
\t\t\t\talgo = "crc32";
\t\t\t};
\t\t};
\t\tpadding {
\t\t\tdescription = "Padding for minimum size";
\t\t\tdata = /incbin/("/tmp/pad32k.bin");
\t\t\ttype = "ramdisk";
\t\t\tcompression = "none";
\t\t};
\t};

\tconfigurations {
\t\tdefault = "config-1";
\t\tconfig-1 {
\t\t\tdescription = "Restore Slot 1";
\t\t};
\t};
};
"""

with open("/tmp/restore.its", "w") as f:
    f.write(its_content)

out_path = f"{tools_dir}/restaurar_slot1_acer.itb"
res = subprocess.run(["mkimage", "-f", "/tmp/restore.its", out_path], capture_output=True, text=True)
print("mkimage STDOUT:", res.stdout)
print("mkimage STDERR:", res.stderr)

# Also copy to root of tools as restaurar_acer.itb
subprocess.run(["cp", out_path, f"{tools_dir}/restaurar_acer.itb"], check=True)
print("Updated restaurar_acer.itb successfully!")
