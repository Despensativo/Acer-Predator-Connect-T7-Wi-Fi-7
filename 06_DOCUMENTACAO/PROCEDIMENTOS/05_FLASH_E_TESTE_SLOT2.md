# Procedimento 05: Gravação de Teste no Slot 2 (Seguro)

> **Status:** [VALIDADO TEORICAMENTE / AGUARDANDO ENSAIO EM BANCADA]  
> **Nível de Risco:** [MÉDIO - Gravação no Slot 2 | Slot 1 OEM Preservado]  
> **Objetivo:** Gravar a imagem compilada de RootFS na partição secundária (`rootfs_1` / `mtd20`) e chavear o bootloader para testar sem risco de perder o firmware de fábrica.

---

## 1. Pré-requisitos Obrigatórios

- [ ] Backups de `mtd3` (`BOOTCONFIG`), `mtd4` (`BOOTCONFIG1`) e `mtd18` (`ART`) salvos no PC.
- [ ] Confirmação de que o Slot 1 (`mtd21`) está ativo e saudável.
- [ ] Conexão cabeada direta (porta LAN 1) e cabo serial UART preparado (se disponível).

---

## 2. Envio da Imagem para o Roteador

No seu computador:
```powershell
scp -O rootfs_custom.bin Admin@192.168.73.2:/tmp/rootfs_custom.bin
```

---

## 3. Gravação Exclusiva na Partição Secundária (Slot 2)

No terminal do roteador:

```sh
# 1. Conferir se o arquivo chegou íntegro em /tmp:
ls -l /tmp/rootfs_custom.bin

# 2. Desbloquear a partição secundária (mtd20):
mtd unlock /dev/mtd20

# 3. Gravar a nova imagem na partição rootfs_1:
mtd write /tmp/rootfs_custom.bin /dev/mtd20

# 4. Sincronizar buffers da memória Flash:
sync
```

> [!CAUTION]
> **NUNCA execute `mtd write` no `/dev/mtd21`**. O `mtd21` é o seu Slot 1 de fábrica, a única garantia de inicialização se a imagem customizada falhar.

---

## 4. Chaveamento do Boot para o Slot 2

Após a gravação bem-sucedida do `mtd20`:

```sh
# Executar o chaveador nativo da Acer:
/usr/sbin/boot-openwrt
```
*Este comando altera `primaryboot=0` nas partições `BOOTCONFIG`, define `fsbootargs` para `rootfs_1` e reinicia o aparelho.*

---

## 5. Procedimento de Retorno ao Slot 1 (Rollback)

Se a imagem do Slot 2 subir com acesso ao terminal, retorne a qualquer momento com:
```sh
/usr/sbin/boot-acer
```
*(Remove `fsbootargs`, restaura `primaryboot=1` e reinicia no firmware oficial de fábrica).*
