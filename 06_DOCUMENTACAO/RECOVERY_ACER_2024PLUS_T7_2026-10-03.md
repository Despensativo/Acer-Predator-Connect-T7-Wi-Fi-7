# Recuperação Acer recente (2024+) versus Predator Connect T7

Pesquisa de 2026-10-03. Fontes públicas oficiais Acer e documentação/código primário OpenWrt, cruzadas com backups locais do T7. Nenhum teste no roteador, servidor TFTP ou alteração de rede foi feito.

## Comparação

| Equipamento/caminho | Plataforma | IP do roteador / IP do servidor | Arquivo e ação | Natureza da evidência |
| --- | --- | --- | --- | --- |
| Predator Connect W6x, U-Boot de fábrica | MediaTek MT7986 | `192.168.1.1` / `192.168.1.66` | `predator.bin`; interromper boot no console serial, executar `setenv` e `tftpboot 0x46000000 ...; bootm` | Procedimento OpenWrt publicado em commit de 2025. Os IPs são atribuídos manualmente, não descoberta automática comprovada. |
| Connect Vero W6m, U-Boot de fábrica | MediaTek MT7986 | `192.168.1.1` / `192.168.1.66` | `vero.bin`; console serial, `setenv`, `tftpboot 0x46000000`, `bootm`; há etapas específicas de assinatura/ambiente | Página do dispositivo OpenWrt; não é procedimento Qualcomm/T7. |
| W6x com U-Boot **modificado** OpenWrt | MediaTek MT7986 | `192.168.1.1` / `192.168.1.254` | Nome completo `openwrt-mediatek-filogic-acer_predator-w6x-ubootmod-initramfs-recovery.itb`; fallback automático TFTP após falha de boot | Valores codificados no ambiente da versão ubootmod. Não existem por inferência no U-Boot Acer de fábrica. |
| Predator Connect T7, firmware OEM | Qualcomm IPQ53xx | `192.168.76.1` na LAN normal (manual Acer); HTTP Failsafe observado localmente em `192.168.1.1`; backup APPSBLENV informa `ipaddr=192.168.10.1`, `serverip=192.168.10.10` | `bootcmd=bootipq`; APPSBL contém `tftpboot`, `bootm`, `source` e ramo HTTP de script FIT. Nenhum nome TFTP automático foi demonstrado. | Manual Acer + leituras estáticas/backup do T7. Os três contextos de IP são diferentes. |

O X7 compartilha componentes de boot com o T7 nos pacotes comparados localmente, mas não foi encontrada nesta pesquisa uma instrução pública primária de recuperação TFTP específica do X7 que estabeleça IP/arquivo/autostart. Não extrapolar do reset/FOTA do X7.

## Fontes

- [Commit OpenWrt W6x stock, 2025](https://git.openwrt.org/6e04dccb7ad3191e9a48597a1b354bf548ead1d8) e [texto do commit](https://lists.infradead.org/pipermail/lede-commits/2025-August/026748.html).
- [OpenWrt: Acer Connect Vero W6m](https://openwrt.org/toh/acer/predator_vero_w6m).
- [OpenWrt: recuperação Filogic ubootmod](https://openwrt.org/inbox/filogic_ubootmod_recovery) e [código de ambiente W6x ubootmod](https://git.openwrt.org/openwrt/staging/nbd/tree/package/boot/uboot-mediatek/patches/465-add-acer_predator-w6x.patch).
- [Manual oficial do T7](https://global-download.acer.com/GDFiles/Document/User%20Manual/User%20Manual_Acer_1.0_A_A.pdf?BC=ACER&LC=en&OS=ALL&SC=EMEA_27&Step3=PREDATOR+CONNECT+T7+WI-FI+7+MESH+ROUTER&acerid=638591363874663059), páginas 5 e 33; apresenta IP de administração/LAN, não IP do bootloader.
- Evidência local T7: `06_DOCUMENTACAO/logs_e_rascunhos/relatorios_auditoria_outubro_2026/BOOT-RAM-TFTP-VERIFICACAO-2026-10-02.md`, `LEVANTAMENTO-MEMORIA-BOOT-RAM-2026-10-02.md`, backup APPSBLENV e `BOOT_PATH_STATIC.md` do protótipo atual.

## Decisão para o T7

**Fato observado:** `192.168.1.66` é uma escolha manual documentada em roteadores Acer MediaTek, não um padrão universal Acer. O `.254` é do bootloader modificado. O manual do T7 usa `.76.1` para administração normal; isso não determina o endereço do Failsafe nem o TFTP. O backup do T7 conserva `.10.1/.10.10`, mas não confirma o ambiente volátil da recuperação HTTP.

**Inferência:** se o T7 executar o script FIT HTTP que define `ipaddr=192.168.1.1` e `serverip=192.168.1.5`, a troca TFTP deverá usar esses endereços, não `.66` nem `.254`. Isso depende de o script realmente ser interpretado e da porta Ethernet ativa.

**Precisa confirmar:** se existe TFTP automático no T7, qual interface física responde no Failsafe, se o script HTTP é executado no firmware atual e se os comandos de rede alcançam o PC. O passo informativo é uma única captura passiva de ARP/UDP 69 na porta física correta durante entrada controlada no Failsafe. Ausência de solicitação TFTP indica apenas que não foi observada naquele contexto; não prova ausência universal. Depois, uma sonda curta e identificada pode testar a execução do ramo HTTP, sob autorização específica e com plano de recuperação.

**Não fazer:** variar IPs/nomes por tentativa, servir `predator.bin` por mera analogia, enviar o FIT do kernel diretamente à página HTTP, executar comandos W6x de alteração de assinatura/slot/U-Boot no T7, nem presumir fallback automático.
