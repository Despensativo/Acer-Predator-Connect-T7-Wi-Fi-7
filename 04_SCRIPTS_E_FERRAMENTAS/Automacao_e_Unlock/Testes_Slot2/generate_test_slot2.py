import os
import subprocess

base_dir = r"/mnt/h/FEITOS COM IA/Acer-Predator-Connect-T7"
tools_dir = f"{base_dir}/3 - Ferramentas de Recuperacao"
desktop_dir = r"/mnt/c/Users/User/Desktop"

# IMPORTANT: imgaddr in U-Boot failsafe is 0x44000000 (where this script lives).
# Therefore, we MUST load the kernel at 0x45000000 so it does not overwrite the running script!
cmd_script = """echo ========================================================
echo INICIANDO TESTE DO SLOT 2 (OPENWRT DIRETO EM RAM)
echo ========================================================
echo [1/5] Selecionando dispositivo NAND...
nand device 0
echo [2/5] Mapeando particao fs no offset do Slot 2 (0x10640000)...
setenv mtdids nand0=nand0
setenv mtdparts mtdparts=nand0:0xf000000@0x10640000(fs)
echo [3/5] Montando UBI fs...
ubi part fs
echo [4/5] Lendo kernel do Slot 2 para RAM livre (0x45000000)...
ubi read 0x45000000 kernel
echo [5/5] Configurando bootargs para Slot 2 (rootfs_1)...
setenv bootargs console=ttyMSM0,115200n8 ubi.mtd=rootfs_1 root=mtd:ubi_rootfs rootfstype=squashfs rootwait vmalloc=1G
setenv config_name config@mi01.6
echo ========================================================
echo EXECUTANDO KERNEL DO SLOT 2 (0x45000000#config@mi01.6)...
echo ========================================================
bootm 0x45000000#config@mi01.6
echo ========================================================
echo [AVISO] Se chegou aqui, o boot falhou. Reiniciando em 5s...
echo ========================================================
sleep 5
reset
"""

with open("/tmp/boot_slot2.scr", "w") as f:
    f.write(cmd_script)

# Create 32KB padding
with open("/tmp/pad32k.bin", "wb") as f:
    f.write(b"\x00" * 32768)

its_content = """/dts-v1/;

/ {
\tdescription = "Flash Test Slot 2";
\t#address-cells = <1>;

\timages {
\t\tscript {
\t\t\tdescription = "Direct Boot Slot 2 Script";
\t\t\tdata = /incbin/("/tmp/boot_slot2.scr");
\t\t\ttype = "script";
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
\t\t\tdescription = "Boot Slot 2";
\t\t};
\t};
};
"""

with open("/tmp/boot_slot2.its", "w") as f:
    f.write(its_content)

out_tools = f"{tools_dir}/testar_boot_slot2.itb"
res = subprocess.run(["mkimage", "-f", "/tmp/boot_slot2.its", out_tools], capture_output=True, text=True)
print("mkimage STDOUT:", res.stdout)
print("mkimage STDERR:", res.stderr)

# Also copy directly to Windows Desktop
out_desktop = f"{desktop_dir}/testar_boot_slot2.itb"
subprocess.run(["cp", out_tools, out_desktop], check=True)
print(f"Arquivo atualizado com sucesso em:")
print(f" -> {out_tools}")
print(f" -> {out_desktop}")
