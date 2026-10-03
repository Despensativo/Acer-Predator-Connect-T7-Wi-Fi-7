# Procedimento 01: Dumps e Backups de Partições MTD

> **Status:** [VALIDADO EM BANCADA]  
> **Nível de Risco:** [NENHUM - Apenas Leitura]  
> **Objetivo:** Extrair cópias de segurança byte a byte de todas as partições da memória Flash antes de qualquer modificação de ROM.

---

## 1. Partições de Prioridade Crítica

Antes de alterar qualquer arquivo, garanta cópias locais das seguintes partições:

| Partição | MTD Device | Finalidade | Risco de Perda |
| :--- | :--- | :--- | :--- |
| `0:ART` | `/dev/mtd18` | Calibração de rádio Wi-Fi e MAC | **Irrecuperável sem backup** |
| `0:APPSBL` | `/dev/mtd11` | Bootloader U-Boot | Alto (Exige JTAG/Gravadora) |
| `0:APPSBLENV` | `/dev/mtd13` | Variáveis de ambiente U-Boot | Alto |
| `BOOTCONFIG` | `/dev/mtd3` | Seletor de Slot Primário | Médio (Pode ser reescrito) |
| `BOOTCONFIG1` | `/dev/mtd4` | Seletor de Slot Secundário | Médio |

---

## 2. Extração Individual via Terminal

Acesse o roteador via SSH/Telnet e execute:

```sh
# Extrair calibração de rádio (ART)
cat /dev/mtd18 > /tmp/backup_art.bin

# Extrair U-Boot e variáveis
cat /dev/mtd11 > /tmp/backup_appsbl.bin
cat /dev/mtd13 > /tmp/backup_appsblenv.bin

# Extrair seletores de boot
cat /dev/mtd3 > /tmp/backup_bootconfig.bin
cat /dev/mtd4 > /tmp/backup_bootconfig1.bin
```

---

## 3. Extração Completa Automatizada de Todos os MTDs

Para despejar todos os 35 MTDs de uma só vez para `/tmp/`:

```sh
mkdir -p /tmp/mtd_dumps
for i in $(seq 0 34); do
  if [ -e "/dev/mtd$i" ]; then
    cat "/dev/mtd$i" > "/tmp/mtd_dumps/mtd${i}.bin" 2>/dev/null
  fi
done
```

---

## 4. Download para o PC e Validação de Hash

No computador (PowerShell):

```powershell
# Copiar pasta de dumps para o PC
scp -r Admin@192.168.73.2:/tmp/mtd_dumps/ "H:\FEITOS COM IA\Acer-Predator-Connect-T7\Backups_MTD\Dump_Recente"

# Gerar hashes de integridade
Get-FileHash -Algorithm SHA256 "H:\FEITOS COM IA\Acer-Predator-Connect-T7\Backups_MTD\Dump_Recente\*.bin"
```

> [!TIP]
> Nunca salve apenas uma cópia. Mantenha os arquivos de `02_BACKUPS_E_DUMPS/MTD_Full_Dumps/` sincronizados em armazenamento secundário ou nuvem.
