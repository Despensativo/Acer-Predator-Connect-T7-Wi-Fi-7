#!/bin/sh
set -e

echo "================================================================="
echo "   PREDATOR CONNECT T7 - ENGINE DE FLASH INTELIGENTE QUALCOMM    "
echo "================================================================="

# 1. Identificar slot ativo e determinar slot alvo livre
ACTIVE_ROOTFS=$(grep -o 'ubi.mtd=[^ ]*' /proc/cmdline | cut -d= -f2)
UPGRADE_PART=$(cat /proc/boot_info/bootconfig0/rootfs/upgradepartition 2>/dev/null || echo "")
CURRENT_PB=$(cat /proc/boot_info/bootconfig0/rootfs/primaryboot 2>/dev/null || echo "1")

echo "[*] Diagnostico de Boot:"
echo "    - RootFS em execucao: $ACTIVE_ROOTFS"
echo "    - Upgrade Partition declarada: $UPGRADE_PART"
echo "    - PrimaryBoot atual: $CURRENT_PB"

if [ "$ACTIVE_ROOTFS" = "rootfs" ] || [ "$UPGRADE_PART" = "rootfs_1" ]; then
    TARGET_SLOT="SLOT 2 (rootfs_1)"
    TARGET_MTD="20"
    NEW_PB="0"
    ACTIVE_SLOT_NAME="SLOT 1 (rootfs)"
elif [ "$ACTIVE_ROOTFS" = "rootfs_1" ] || [ "$UPGRADE_PART" = "rootfs" ]; then
    TARGET_SLOT="SLOT 1 (rootfs)"
    TARGET_MTD="21"
    NEW_PB="1"
    ACTIVE_SLOT_NAME="SLOT 2 (rootfs_1)"
else
    echo "[-] ERRO: Nao foi possivel determinar o slot ativo com seguranca."
    exit 1
fi

echo "[+] Slot ativo detectado: $ACTIVE_SLOT_NAME"
echo "[+] Gravando no slot livre: $TARGET_SLOT (MTD $TARGET_MTD)"
echo "[+] Novo PrimaryBoot que sera ativado: $NEW_PB"

# 2. Anexar o MTD alvo como UBI1
echo ""
echo "=== [1/6] ANEXANDO MTD $TARGET_MTD COMO UBI1 ==="
ubidetach /dev/ubi_ctrl -d 1 2>/dev/null || true
ubiattach /dev/ubi_ctrl -m "$TARGET_MTD" -d 1

# Garantir criacao dos nos de dispositivo em /dev
for v in /sys/class/ubi/ubi1_*; do
    [ -d "$v" ] && mknod "/dev/$(basename "$v")" c $(cat "$v/dev" | tr : ' ') 2>/dev/null || true
done

# Validar presenca dos 4 volumes
for vol in ubi1_0 ubi1_1 ubi1_2 ubi1_3; do
    if [ ! -e "/dev/$vol" ]; then
        echo "[-] ERRO: Dispositivo /dev/$vol nao encontrado apos ubiattach."
        ubidetach /dev/ubi_ctrl -d 1 2>/dev/null || true
        exit 1
    fi
done

VOL0_NAME=$(cat /sys/class/ubi/ubi1_0/name 2>/dev/null || echo "unknown")
VOL1_NAME=$(cat /sys/class/ubi/ubi1_1/name 2>/dev/null || echo "unknown")
VOL2_NAME=$(cat /sys/class/ubi/ubi1_2/name 2>/dev/null || echo "unknown")
VOL3_NAME=$(cat /sys/class/ubi/ubi1_3/name 2>/dev/null || echo "unknown")

echo "    [OK] Volumes mapeados com sucesso:"
echo "         /dev/ubi1_0 -> $VOL0_NAME"
echo "         /dev/ubi1_1 -> $VOL1_NAME"
echo "         /dev/ubi1_2 -> $VOL2_NAME"
echo "         /dev/ubi1_3 -> $VOL3_NAME"

# 3. Gravar Componente 1: Wi-Fi Firmware
echo ""
echo "=== [2/6] GRAVANDO WI-FI FIRMWARE (wifi_fw.bin -> /dev/ubi1_0) ==="
if [ ! -f /tmp/wifi_fw.bin ]; then
    echo "[-] ERRO: /tmp/wifi_fw.bin nao encontrado!"
    ubidetach /dev/ubi_ctrl -d 1 2>/dev/null || true
    exit 1
fi
ubiupdatevol /dev/ubi1_0 /tmp/wifi_fw.bin
echo "    [OK] Wi-Fi Firmware gravado com sucesso."

# 4. Gravar Componente 2: Kernel Linux
echo ""
echo "=== [3/6] GRAVANDO KERNEL LINUX (kernel.bin -> /dev/ubi1_1) ==="
if [ ! -f /tmp/kernel.bin ]; then
    echo "[-] ERRO: /tmp/kernel.bin nao encontrado!"
    ubidetach /dev/ubi_ctrl -d 1 2>/dev/null || true
    exit 1
fi
ubiupdatevol /dev/ubi1_1 /tmp/kernel.bin
echo "    [OK] Kernel Linux gravado com sucesso."

# 5. Gravar Componente 3: RootFS Otimizado
echo ""
echo "=== [4/6] GRAVANDO ROOTFS SQUASHFS (rootfs.squashfs -> /dev/ubi1_2) ==="
if [ ! -f /tmp/rootfs.squashfs ]; then
    echo "[-] ERRO: /tmp/rootfs.squashfs nao encontrado!"
    ubidetach /dev/ubi_ctrl -d 1 2>/dev/null || true
    exit 1
fi
ubiupdatevol /dev/ubi1_2 /tmp/rootfs.squashfs
echo "    [OK] RootFS gravado com sucesso."

# 6. Limpar particao de Overlay de dados (rootfs_data)
echo ""
echo "=== [5/6] FORMATANDO OVERLAY LIMPO (/dev/ubi1_3) ==="
ubiupdatevol /dev/ubi1_3 -t
echo "    [OK] Overlay formatado limpo (sem sobras ou conflitos de versoes antigas)."

# 7. Validacao do sistema gravado
echo ""
echo "=== [6/6] VALIDANDO SISTEMA DE ARQUIVOS GRAVADO NA FLASH ==="
ubiblock -c /dev/ubi1_2 2>/dev/null || true
mkdir -p /tmp/chk_val
mount -t squashfs /dev/ubiblock1_2 /tmp/chk_val

VER_GRAVADA=$(cat /tmp/chk_val/etc/version 2>/dev/null || echo "desconhecida")
echo "    [+] Versao gravada na NAND: $VER_GRAVADA"
echo "    [+] Permissoes de cgi-io: $(ls -ld /tmp/chk_val/usr/libexec/cgi-io 2>/dev/null)"
echo "    [+] Permissoes de /www/cgi-bin: $(ls -ld /tmp/chk_val/www/cgi-bin 2>/dev/null)"

if [ -f /tmp/chk_val/usr/sbin/smbd ]; then
    echo "[-] ALERTA: Samba detectado na imagem gravada!"
else
    echo "    [OK] Confirmado: Sistema limpo e livre de Samba."
fi

umount /tmp/chk_val
ubiblock -r /dev/ubi1_2 2>/dev/null || true
rm -rf /tmp/chk_val

# 8. Desanexar UBI1 e liberar RAM (nao fatal se o kernel ja tiver liberado)
ubidetach -d 1 2>/dev/null || ubidetach -m "$TARGET_MTD" 2>/dev/null || true
rm -f /tmp/wifi_fw.bin /tmp/kernel.bin /tmp/rootfs.squashfs /tmp/flash_engine.sh

# 9. Chaveamento do BootConfig Qualcomm
echo ""
echo "=== ATUALIZANDO BOOTCONFIG QUALCOMM PARA $TARGET_SLOT (PRIMARYBOOT = $NEW_PB) ==="
echo "$NEW_PB" > /proc/boot_info/bootconfig0/rootfs/primaryboot
echo "$NEW_PB" > /proc/boot_info/bootconfig1/rootfs/primaryboot
cat /proc/boot_info/bootconfig0/getbinary_bootconfig > /tmp/bc0.bin
cat /proc/boot_info/bootconfig1/getbinary_bootconfig > /tmp/bc1.bin
mtd unlock /dev/mtd3 2>/dev/null || true
mtd unlock /dev/mtd4 2>/dev/null || true
mtd -e /dev/mtd3 write /tmp/bc0.bin /dev/mtd3
mtd -e /dev/mtd4 write /tmp/bc1.bin /dev/mtd4
rm -f /tmp/bc0.bin /tmp/bc1.bin
sync

echo ""
echo "================================================================="
echo "   FLASH_CONCLUIDO_COM_SUCESSO! REINICIANDO PARA O $TARGET_SLOT "
echo "================================================================="
sync
reboot
