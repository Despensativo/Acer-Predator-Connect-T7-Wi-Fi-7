# Comparação dos endereços TFTP em roteadores Acer — 2026-10-02

Pesquisa web autorizada pelo usuário; sem novo teste/upload ou alteração no PC/roteador.

## Resultado

Não foi localizada confirmação pública de 192.168.10.1 como endereço TFTP nos outros modelos Acer pesquisados. Os procedimentos OpenWrt para Predator W6, Predator W6x e Connect Vero W6m usam explicitamente setenv ipaddr 192.168.1.1 e setenv serverip 192.168.1.66. Esses são endereços escolhidos no procedimento, não necessariamente padrões de fábrica.

Fonte primária adicional W6x: commit OpenWrt 6e04dccb7ad3191e9a48597a1b354bf548ead1d8, instruções de instalação via UART. Plataforma MediaTek MT7986AV; não transplantar comandos de instalação ou remoção de assinatura para T7 Qualcomm.

Para o próprio T7, há evidência mais direta: leitura atual do arquivo local Backups_MTD/backup_predator_t7_uboot_env.bin confirmou ipaddr=192.168.10.1, serverip=192.168.10.10, netmask=255.255.255.0. ethact/ethprime/ethrotate não aparecem definidos no backup. Evidência filtrada sem dados privados em evidencias/enderecos-tftp-backup-ambiente.json. Isso é backup histórico e não leitura do ambiente volátil em execução no Failsafe.

O HTTP observado em 192.168.1.1 não prova o endereço TFTP. A sonda enviada propõe setenv temporário para 192.168.1.1/192.168.1.5. Sem retorno, sua execução é desconhecida. Não concluir que esses setenv funcionaram nem que o U-Boot força a rede 10.x.

## Recomendação

Capturar ARP/UDP na Ethernet 4, agora que Npcap foi instalado e interface identificada, antes de nova tentativa. A captura deve considerar todos os endereços, incluindo redes 192.168.1.x e 192.168.10.x. Se o bootloader perguntar por 192.168.10.10, isso fundamenta preparar o receptor nessa rede; não trocar IP ou arquivo agora sem evidência e aviso antes do teste.

## Fontes

- W6: https://openwrt.org/toh/acer/predator_w6
- W6x: https://openwrt.org/toh/acer/predator_connect_w6x
- Commit primário W6x: https://lists.infradead.org/pipermail/lede-commits/2025-August/026748.html
- Vero W6m: https://openwrt.org/toh/acer/predator_vero_w6m

Páginas OpenWrt retornaram proteção anti-bot no open, mas os trechos indexados mostraram os procedimentos; W6x foi conferido diretamente no anúncio oficial do commit. Consultas para X7 não localizaram instrução pública de TFTP confirmando 10.1 nas fontes pesquisadas. Ausência de resultado não prova inexistência.
