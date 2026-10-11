# Diagnostico sem UART: variante Ethernet v2

Data: 2026-10-02. Estado: criado, compilado e verificado offline. Nenhum teste no aparelho.

## Resultado

Foi criada uma segunda imagem ARM64 com PPE/EDMA, PCS, MDIO, PHY QCA808x e netconsole built-in. Ela tenta fornecer evidencia positiva de execucao do Linux pela Ethernet, sem depender de raspar trilhas da UART.

Ela nao elimina a cegueira antes de a Ethernet funcionar. Se nao chegar pacote, o resultado permanece inconclusivo quanto a TrustZone e ultima etapa executada.

## O que foi confirmado na arvore local

- O driver QCOM_PPE possui compatible qcom,ipq5332-ppe.
- EDMA possui tabelas especificas para o IPQ5332.
- PCS reconhece qcom,ipq5332-pcs.
- QCA808x inclui o ID QCA8084 0x004dd180, usado no DTS local.
- O driver edma_port_setup usa a propriedade label para nomear interfaces: o DTS fornece lan e wan. Presumir eth0 faria a configuracao de netconsole apontar para um dispositivo inexistente nessa arvore.
- GCC/NSSCC IPQ5332 estao compilados. Isso confirma presenca, nao funcionamento completo dos clocks no aparelho.

As secoes de portas, PCS, MDIO e pinctrl foram derivadas do DTS mainline existente, preservando os arquivos originais. Os GPIOs descritos e o roteamento fisico ainda dependem de validacao no hardware.

## Duas saidas Linux

1. Netconsole built-in tenta enviar printk pela interface lan para o PC em UDP 6667. Pode ajudar apos inicializacao da interface, inclusive antes de /init.
2. /init proprio tenta configurar lan e wan, enviar identificacao em UDP 6666 e retransmitir registros disponiveis de /dev/kmsg. Repete a identificacao para tolerar perda durante negociacao do link.

O init usa configuracao IPv4 local, sem DHCP, DNS ou rota padrao. Nao disponibiliza shell, SSH, Telnet, LuCI ou instalador. O watchdog e alimentado pelo driver convencional se /dev/watchdog estiver disponivel.

Os registros UDP sao limitados: mensagens longas podem ser truncadas e os buffers podem perder registros. Isso nao e uma copia perfeita da UART.

## Identidade e criterio de sucesso

O binario /init contem uma identidade exclusiva desta compilacao, registrada em identidade-net-v2.json. Cada datagrama inclui:

- identidade da compilacao;
- boot_id gerado pelo Linux;
- build t7-net-20261002-v2;
- arquitetura retornada por uname;
- release do kernel;
- interface, fase e sequencia.

O coletor considera evidencia positiva quando recebe INIT_REACHED com identidade esperada, boot_id valido, arch=aarch64 e release 6.18.52-t7-net-20261002-v2.

Um ping, link Ethernet, resposta da Acer, checkpoint TFTP do U-Boot ou pacote avulso de netconsole nao satisfaz esse criterio.

Essa identidade evita confusao acidental com outro firmware; nao e autenticacao criptografica. O ensaio futuro deve usar enlace isolado e considerar os horarios e identificadores do boot.

## Rede candidata para o ensaio futuro

| Uso | Valor candidato |
| --- | --- |
| PC | 169.254.73.1/16 |
| lan do diagnostico | 169.254.73.2/16 |
| wan do diagnostico | 169.254.73.3/16 |
| Identidade e retransmissao kmsg | UDP 6666 |
| Netconsole | UDP 6667 |

Nenhum IP, interface ou firewall do Windows foi alterado. O coletor nao foi iniciado.

O receptor de identidade precisa aceitar broadcast. Por isso a ferramenta futura usa bind wildcard para os listeners, valida o IP local confirmado, filtra remetentes lan/wan e verifica a identidade da compilacao. Ela nao envia comandos ao roteador.

## Binarios e verificacoes

- Image: 11.388.936 bytes.
- image_size ARM64: 11.730.944 bytes.
- FIT: 3.533.400 bytes, aproximadamente 3,37 MiB.
- DTB: 19.995 bytes.
- Init estatico: 308.280 bytes.
- No endereco candidato 0x41000000, o intervalo requerido termina em 0x41b30000.

FIT SHA-256: 76d8a9969cd44b723ac9e4e092a9f27aad08a84f61be126d7af7d7b537ed3373.

Verificacao independente confirmou FIT, CRC dos dois payloads, LZMA, cabecalho ARM64, DTB, initramfs de seis entradas, init estatico, identidade embutida e opcoes de rede como built-in. Simbolos qcom_ppe_probe e init_netconsole estao presentes.

Quatro testes do parser em memoria passaram, rejeitando identidade errada, arquitetura errada e boot_id invalido. Nenhum socket foi aberto nos testes.

MTD, modulos, /dev/mem, NVMEM_SYSFS, QFPROM, MMC, SCSI, PCI e USB continuam desativados. Ramoops continua compilado e sem regiao configurada, nao sendo uma saida ativa deste ensaio.

A Image e o FIT v1 permanecem preservados. O scratch isolado foi reutilizado para v2; uma nova copia comprimida das fontes/config foi salva em artefatos/t7-net-20261002-v2. A configuracao original da arvore OpenWrt manteve seu hash anterior.

## Pendencias e limite

- Validar mapa dinamico do U-Boot, limites TFTP, fixups/posicao do DTB e acionador.
- Confirmar Slot 1 e caminho de recuperacao antes de qualquer reset do aparelho.
- Confirmar enlace direto e configuracao do PC antes de iniciar a captura.
- Avisar o usuario antes de qualquer teste no roteador, conforme solicitado.

Manifestos seguem hardware_ready=false. Nao ha acionador ITB de upload liberado.
**Nao enviar o FIT comum ao HTTP Failsafe: pode seguir o caminho OEM de gravacao.**

Se o Linux falhar antes do driver de rede, as alternativas futuras incluem RAM persistente validada ou outro sinal fisico conhecido. Nenhuma delas foi implementada mediante escrita em enderecos/GPIOs presumidos.

## Arquivos

- [Manifesto v2](artefatos/t7-net-20261002-v2/manifesto-candidato.json)
- [Verificacao offline v2](artefatos/t7-net-20261002-v2/verificacao-offline.json)
- [Init com rede](fontes/diag_init_net_v2.c)
- [DTS v2](fontes/t7-diagnostico-net-v2.dts)
- [Coletor](ferramentas/coletar_rede_v2.py)
- [Log final](logs/compilacao-rede-v2-dtb-corrigido.log)

## Fonte oficial

O netconsole envia printk por UDP e, built-in, inicializa apos os dispositivos de rede; ele nao captura os panics mais precoces. [Documentacao do Linux](https://docs.kernel.org/networking/netconsole.html).
