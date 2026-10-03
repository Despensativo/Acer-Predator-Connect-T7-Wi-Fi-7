# Teste futuro: hipótese TFTP Acer em 192.168.1.66

Registrado em 2026-10-02 a pedido do usuário. Nenhum teste, servidor, upload, alteração de ambiente ou reboot autorizado/executado por este registro.

## Informação fornecida para testar depois

Hipótese: U-Boot procura um servidor TFTP em 192.168.1.66 UDP 69, solicita predator.bin (ou bootfile), carrega em RAM em 0x46000000 ou 0x44000000 e executa bootm.

## Estado da evidência

Os procedimentos OpenWrt dos Acer W6/W6x/Vero W6m usam 192.168.1.66 e predator.bin/vero.bin após configurar serverip/ipaddr e executar tftpboot no console. Isso não comprova busca automática, endereço fixo, execução automática de bootm ou comportamento idêntico no T7 Qualcomm IPQ5332.

No backup do próprio T7 e na consulta recente por fw_printenv: ipaddr=192.168.10.1, serverip=192.168.10.10. Failsafe HTTP observado em 192.168.1.1. Não confundir esses serviços e contextos. O comando de boot observado é bootipq.

## Como considerar essa hipótese futuramente

Primeiro capturar ARP/UDP na Ethernet 4 antes de uma tentativa revisada para identificar destinos reais e nomes de arquivos pedidos. Preparar servidor 192.168.1.66 somente se a captura/configuração revista fundamentar isso. Não servir automaticamente predator.bin enquanto autostart, bootm, destino RAM e caminho de recuperação não forem validados. 0x44000000 é buffer HTTP conhecido e não está aprovado para carga do kernel; 0x46000000 também depende de validação do mapa real. Avisar o usuário antes de qualquer teste no hardware.

Não alterar bootcmd, saveenv ou partições para testar esta hipótese. Prioridade atual: Slot 1 preservado, Slot 2 com hashes iguais ao Slot 1 e overlay vazio; boot do Slot 2 ainda não testado.

Fonte primária para o procedimento W6x: https://lists.infradead.org/pipermail/lede-commits/2025-August/026748.html
