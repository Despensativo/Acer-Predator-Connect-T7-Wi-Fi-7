# Pesquisa da porta física TFTP do Acer T7 — 2026-10-02

Escopo: pesquisa web e leitura dos arquivos locais. Nenhum novo upload ou mudança no roteador/PC.

## Resultado

Não foi localizada nas fontes consultadas uma indicação verificável de conector físico obrigatório para tftpboot/tftpput no Acer Predator Connect T7. Não afirmar LAN 1, Game ou WAN como porta correta com base em outro aparelho. A existência de porta exclusiva permanece hipótese, não diagnóstico da sonda sem retorno.

O manual oficial Acer descreve WAN/LAN, Game e LAN, mas não contém referência textual a TFTP. A documentação oficial U-Boot descreve ethprime (primeira interface), ethact (interface atual) e ethrotate (rotação), sem mapear conectores deste modelo OEM. O dump local contém as três strings, junto de ipq5332_eth_init e eth0 PHY%d; strings não bastam para mapear interface/PHY ao conector.

Dump SHA-256 3d6281190512ba50b83eea1a2d6fca69f01da5bb390d52b601e762ce8f1df2fc. Strings: ethact 0x6a85d, ethprime 0x6a8e4, ethrotate 0x6a864, eth0 PHY%d 0x6cd1a. tftpboot/tftpput foram confirmados separadamente na tabela de comandos em evidencias/confirmacao-comandos-tftp-uboot.json.

Foi encontrado o repositório Despensativo/Acer-Predator-Connect-T7-Wi-Fi-7, com nomes de arquivos, backups e contexto coincidentes com este projeto. Não tratá-lo como confirmação independente de ensaio de TFTP. Resultados para Predator W6/W6x são de outra plataforma e não definem a porta do T7. Relatos de Xiaomi/GL com IPQ5332 também não comprovam o cabeamento Acer; análises de IA de outros repositórios não foram usadas como prova.

O backup local de ambiente contém ipaddr=192.168.10.1 e serverip=192.168.10.10. O HTTP Failsafe foi observado em 192.168.1.1. A sonda propõe setenv temporário para 192.168.1.1/192.168.1.5; sem comprovar execução, não é possível inferir o IP efetivo do TFTP pelo IP HTTP. O usuário tinha razão ao distinguir as redes possíveis.

## Próximo diagnóstico

Captura ARP/UDP na Ethernet 4 antes de qualquer novo teste, com registro de todos os IPs envolvidos, distinguindo ausência de tráfego, endereço inesperado, handshake TFTP e falha de protocolo. Confirmar o mecanismo de captura disponível no PC (Wireshark/dumpcap não encontrado no caminho habitual e sessão sem privilégios administrativos). Só depois considerar comparação controlada dos conectores, sem nova gravação persistente.

## Fontes consultadas

- https://docs.u-boot.org/en/latest/usage/environment.html
- https://docs.u-boot.org/en/latest/usage/cmd/tftpput.html
- https://github.com/Despensativo/Acer-Predator-Connect-T7-Wi-Fi-7
- Manual oficial Acer: https://global-download.acer.com/GDFiles/Document/User%20Manual/User%20Manual_Acer_1.0_A_A.pdf?BC=ACER&LC=en&OS=ALL&SC=PA_4&Step3=PREDATOR+CONNECT+T7+WI-FI+7+MESH+ROUTER&acerid=638591363874663059

## Estado do teste existente

Imagem do usuário confirma que o upload HTTP foi recebido. Não foi recebida prova TFTP da sonda até a última verificação; Failsafe permaneceu acessível e firmware normal não respondeu naquela verificação. Isso não comprova falta de TFTP, porta LAN incorreta, gravação de firmware ou falha ARM64.
