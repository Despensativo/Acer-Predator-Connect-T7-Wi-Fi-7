# Levantamento de memória e diagnóstico por rede — Acer Predator T7

Data: 02/10/2026.
Escopo: análise estática dos arquivos preservados. Nenhum acesso ao roteador, instalação, compilação, servidor iniciado ou alteração de fontes/configurações/imagens. Documentação nova apenas.

## Resultado

Existe um caminho plausível para preparar um boot temporário sem UART: HTTP executa o acionador FIT; o acionador usa TFTP para receber a imagem e bootm para iniciar. A seleção especial do Failsafe foi documentada em BOOT-RAM-TFTP-VERIFICACAO-2026-10-02.md.

Esta etapa acrescenta três resultados:
1. Um mapa conservador das reservas OEM e um arranjo provisório para uma futura imagem mínima.
2. Um mecanismo possível de checkpoints por TFTP, graças à presença de tftpput.
3. Novas inconsistências: tamanho de RAM divergente entre DTBs, extração inválida do DTB do U-Boot, servidor TFTP com fallback perigoso e earlycon proposto incompatível com os DTBs.

Não existe ainda um endereço comprovadamente seguro para usar no aparelho. Os intervalos candidatos abaixo são planejamento, não comandos prontos para execução.

## RAM: o que foi observado e o que falta confirmar

| Artefato | Base | Tamanho declarado | Fim exclusivo |
| --- | --- | --- | --- |
| Engenharia_Reversa_OpenWrt/acer_predator_t7.dtb | 0x40000000 | 1 GiB | 0x80000000 |
| Backups_MTD/stock_mi01_6.dtb | 0x40000000 | 512 MiB | 0x60000000 |
| DTBs mainline auditados | 0x40000000 | zero, esperando fixup | sem fim utilizável |

O DTB OEM de 1 GiB também contém propriedades de versões de boot/TZ e bootargs preenchidos; o de 512 MiB não tem essas mesmas propriedades. Isso é compatível com diferenças entre template e árvore alterada no boot, mas a procedência exata de cada captura precisa ser confirmada. Não comprova isoladamente que o bootloader corrige qualquer DTB mainline.

Os intervalos candidatos ficam abaixo de 0x60000000 e, portanto, dentro dos dois tamanhos OEM declarados. Isso evita depender da RAM acima de 512 MiB, mas não comprova ausência de buffers ou outras reservas na região escolhida. Não alterar o nó memory para 1 GiB somente com base na etiqueta da placa ou no DTB arquivado.

## Reservas OEM

Intervalos em formato [início, fim): o fim não pertence à reserva.

| Região | Início | Fim exclusivo | Observação |
| --- | --- | --- | --- |
| tzapp | 0x49b00000 | 0x4a100000 | aplicação segura |
| uboot | 0x4a100000 | 0x4a500000 | reserva do bootloader |
| sbl | 0x4a500000 | 0x4a600000 | firmware de boot |
| tz | 0x4a600000 | 0x4a800000 | TrustZone |
| smem | 0x4a800000 | 0x4a900000 | memória compartilhada |
| wcnss | 0x4a900000 | 0x4cc00000 | firmware de rádio |
| m3_dump | 0x4cc00000 | 0x4cd00000 | não usar para ramoops |
| q6_etr_dump | 0x4cd00000 | 0x4ce00000 | dump do coprocessador |
| q6_caldb_region | 0x4ce00000 | 0x4d300000 | calibração |
| mlo_global_mem_0 | 0x4db00000 | 0x4ec00000 | memória MLO |
| qcn9224_pcie0 | 0x4ec00000 | 0x51e00000 | disabled no DTB; manter excluída conservadoramente |
| qcn9224_pcie1 | 0x51e00000 | 0x55000000 | ativa |

Há ainda dois pools shared-dma-pool sem reg fixo, cada um com size de 9 MiB. Seu posicionamento depende de alocação em execução.

Para o planejamento inicial, excluir todo [0x49b00000, 0x55000000), incluindo lacunas entre as reservas, até compreender seu uso. A ausência de um nó reservado não equivale a memória livre.

Os DTBs dos ITBs mainline de initramfs examinados conservam bootloader, SBL, TZ e SMEM, mas não reproduzem todas as reservas OEM acima, inclusive tzapp. Isso precisa ser resolvido antes de considerar a memória restante disponível ao kernel. Remover suporte de rádio do kernel não prova que o firmware anterior deixou de usar essas regiões.

## Onde o bootloader está ligado

O APPSBL é ELF de 32 bits. Seu segmento PT_LOAD:
- offset no arquivo: 0x12000;
- endereço virtual e físico: 0x4a400000;
- filesz e memsz: 0x78048;
- fim exclusivo: 0x4a478048.

Esse segmento cabe na reserva OEM uboot. Entretanto o cabeçalho ELF não descreve necessariamente toda a RAM utilizada durante a recuperação, incluindo heap, pilha, global data e buffers de rede. Não usar o segmento ELF como limite completo da ocupação do U-Boot.

## DTB do U-Boot anteriormente extraído: inválido

O script extract_uboot_dtb.py assume que há um DTB no offset 0x520d0. No dump examinado:
- o primeiro word é d00dfeed;
- o totalsize lido é 0x00280cdc, maior que o restante do arquivo;
- os demais offsets do cabeçalho também estão fora do blob;
- o parser não consegue construir a árvore;
- a varredura local não encontrou um cabeçalho FDT completo e válido no APPSBL, usando verificação de limites e versões 16/17.

O arquivo /home/builder/uboot.dtb preservado tem 1.236.784 bytes e o mesmo cabeçalho inválido. A extração anterior reconheceu uma sequência magic, mas não validou o cabeçalho.

Não executar o extrator para refazer o arquivo nem usar essa suposta árvore como evidência de bancos de RAM ou reservas. Isso não demonstra que o U-Boot não possui árvore de controle: ela pode ser construída ou obtida de outra origem.

## Limite de descompressão encontrado no binário

Em 0x4a409aba o caminho de carga do sistema prepara 0x04000000, ou 64 MiB. Em 0x4a409ac2 coloca esse valor como argumento na pilha e em 0x4a409ad2 chama o auxiliar de cópia/descompressão 0x4a409998.

O initramfs atual tem Image de 52.533.256 bytes e image_size de 0x03270000. Ambos são inferiores a 64 MiB. Logo, nesse caminho estático, não há evidência de que ele exceda o limite passado ao descompressor. Isso não resolve a sobreposição de endereços nem outras restrições de memória.

O caminho LZMA chama 0x4a43afe4, usando o limite de saída passado. A presença da mensagem "Image too large: increase CONFIG_SYS_BOOTM_LEN" sozinha não demonstra que esse erro ocorreu.

## Arranjo provisório para uma futura imagem mínima

| Uso | Início candidato | Fim exclusivo planejado | Limite de planejamento |
| --- | --- | --- | --- |
| Image com initramfs embutido | 0x41000000 | 0x43000000 | image_size e saída descomprimida até 32 MiB |
| Acionador recebido pelo HTTP | 0x44000000 | 0x44010000 | até 64 KiB |
| Pequeno buffer de checkpoints | 0x45000000 | 0x45001000 | até 4 KiB |
| FIT recebido pelo TFTP | 0x46000000 | 0x47000000 | até 16 MiB |
| DTB final e workspace de boot | ainda não definido | ainda não definido | respeitar fixups e alocação OEM |

Esse arranjo separa o acionador, o FIT comprimido e o destino do kernel. O endereço 0x41000000 satisfaz o alinhamento de 2 MiB para text_offset=0 dos Images examinados.

O initramfs atual não cabe no orçamento de 32 MiB: ele terminaria em 0x44270000 e intersectaria o acionador. A tabela serve para projetar um initramfs menor; não autoriza reutilizar o atual.

fdt_high=0x48500000 aparece no backup de ambiente. É um limite superior usado na colocação do DTB, não um endereço final confirmado. Não escolher arbitrariamente esse endereço como destino nem supor que o espaço abaixo dele esteja livre.

Antes de aprovar o mapa:
- obter bancos reais e ocupação do U-Boot, inclusive relocaddr, pilha e heap;
- confirmar que o handler HTTP deixa todos os dados necessários fora do destino do kernel;
- definir destino e espaço de expansão do DTB para fixups;
- confirmar que o bootm preserva reservas OEM e não sobrepõe o FIT;
- verificar capacidade exata da imagem antes do download; uma verificação de filesize depois de receber não impede sobrescrita já ocorrida;
- não propor um endereço de ramoops até confirmar exclusividade e persistência através do reset.

## Cópia do script: refinamento do levantamento anterior

O executor em 0x4a41aa36, para comprimento explícito, solicita um buffer de tamanho comprimento+1, copia o texto para esse buffer, acrescenta NUL e passa a cópia ao parser em 0x4a40848c. Libera o buffer após o retorno.

O caminho source para FIT obtém o endereço/tamanho do nó e passa por esse executor. A análise sustenta que o texto do script é copiado antes da interpretação, reduzindo a suspeita de sobrescrita imediata do texto quando o TFTP reutiliza a origem HTTP.

Isso não torna o endereço 0x44000000 adequado ao initramfs anterior nem comprova a localização do buffer alocado. Manter regiões separadas simplifica a revisão e evita depender desse detalhe.

## Diagnóstico por rede sem Netconsole

A tabela de comandos contém tftpput:
- offset da entrada: 0x7bb10;
- função: 0x4a412481;
- limite de argumentos: 4;
- descrição: envio TFTP para um servidor.

Também foram identificados test, itest, setexpr, crc32, cp, md, bdinfo, printenv e fdt. Não foi encontrada uma entrada iminfo na tabela examinada; não basear o acionador nesse comando.

A presença de tftpput permite planejar envio de pequenos blocos conhecidos da RAM para o PC, enquanto o U-Boot ainda controla o hardware. Não transforma stdout serial em Netconsole.

Checkpoints possíveis:
1. ACIONADOR_INICIO: prova que o script iniciou e a troca TFTP chegou ao PC.
2. FIT_RECEBIDO: indica retorno bem-sucedido do comando de recepção; não prova integridade.
3. FIT_VALIDADO: emitido somente após verificar tamanho e integridade esperados.
4. BOOTM_PROXIMO: último marcador antes de chamar o boot.

Se o último marcador for BOOTM_PROXIMO e não houver resposta posterior, só sabemos que o script alcançou esse ponto. A falha pode ocorrer dentro do bootm, na transição ou no kernel.

Formas de emissão a especificar:
- tftpput de um registro curto de status, já inicializado numa região validada;
- pedidos de arquivos pequenos com nomes distintos, registrados pelo servidor TFTP.

A segunda forma prova que o pedido chegou, não necessariamente que a transferência terminou. É obrigatório que cada arquivo exista e tenha tamanho controlado.

Não exportar dumps indiscriminados de RAM: a proposta usa somente buffer de diagnóstico definido, sem conteúdo desconhecido do firmware.

## Problemas do servidor TFTP atual

Em Servidor_TFTP_Windows/tftp_server.py:
- linhas 52–56: se o nome pedido não existe, troca o arquivo por openwrt.itb;
- linhas 162–165: despacha apenas OP_RRQ, leitura;
- OP_WRQ é declarado, mas não há tratamento para receber arquivos enviados por tftpput.

Consequências:
1. Não usar esse servidor inalterado para receber checkpoints por tftpput.
2. Não solicitar marcadores inexistentes em um buffer de 4 KiB: o fallback pode entregar uma imagem de vários MiB e sobrescrever RAM.
3. Para testes futuros, especificar servidor sem fallback, com lista exata de arquivos permitidos, tamanhos conhecidos, WRQ controlado se necessário e registro de IP/nome/tamanho/resultado.
4. Uma linha de log indicando conexão não comprova término da transferência.

Nenhum servidor foi alterado, instalado ou iniciado nesta etapa.

## Inicialização automática e fases do bootm

O backup não define autostart. O comportamento efetivo também depende do default e do código OEM. Antes de planejar um ensaio que apenas recebe a imagem, conferir e bloquear a inicialização automática durante o download, de forma volátil. Não presumir que tftpboot seja sempre apenas carga.

A tabela de subcomandos bootm existe em 0x4a465284 e inclui:
- start, estado 0x1;
- loados, 0x8;
- ramdisk, 0x10;
- fdt, 0x20;
- cmdline, 0x40;
- bdt, 0x80;
- prep, 0x100;
- fake, 0x200;
- go, 0x400.

Isso permite estudar um teste separado em fases, mas não comprova que a rede permanece operacional entre elas. Não chamar prep, fake ou loados como se fossem verificações sem efeitos: podem escrever RAM, alterar DTB ou modificar o estado do hardware.

## UART e earlycon: correção necessária

Os dois DTBs examinados, OEM e mainline initramfs, apontam serial0 para serial@78af000:
- endereço MMIO: 0x078af000;
- tamanho: 0x200;
- compatible inclui qcom,msm-uartdm;
- nó ativo.

No msm_serial.c do Linux 6.18.52 preservado:
- linha 1759: OF_EARLYCON_DECLARE(msm_serial_dm, "qcom,msm-uartdm", ...);
- configuração: CONFIG_SERIAL_EARLYCON=y, CONFIG_SERIAL_MSM=y e CONFIG_SERIAL_MSM_CONSOLE=y.

Portanto earlycon=msm_geni_serial,0xa84000 não corresponde a esses artefatos. Para o plano de UART, avaliar earlycon automático pelo stdout-path ou o nome msm_serial_dm no endereço 0x078af000. A sintaxe e os efeitos devem ser revisados antes de usar; nenhuma mudança foi aplicada.

Isso não confirma os pads físicos, GPIOs ou nível elétrico da placa. A documentação de pinagem precisa ser corroborada separadamente.

## Próximos passos ainda dentro da documentação

1. Especificar o protocolo dos checkpoints e a máquina de estados do acionador, incluindo falhas de TFTP e CRC.
2. Concluir como obter os dados mínimos de memória real e ocupação do bootloader sem exportar informações privadas.
3. Definir os requisitos do servidor TFTP e do FIT mínimo, mantendo o acionador incapaz de gravar flash.
4. Só depois preparar artefatos e validar no hardware, sob autorização explícita para essa nova etapa.

## Referências e evidências

- [U-Boot tftpput](https://docs.u-boot.org/en/latest/usage/cmd/tftpput.html): transferência de memória para servidor.
- [Ambiente U-Boot](https://docs.u-boot.org/en/latest/usage/environment.html): fdt_high, memória de boot e variáveis voláteis/persistentes.
- [Protocolo de boot ARM64](https://docs.kernel.org/arch/arm64/booting.html): alinhamento, image_size e preparação da memória.
- A documentação atual explica a semântica geral; comandos, limites e endereços OEM foram extraídos do dump local.
- Manifesto associado: LEVANTAMENTO-MEMORIA-BOOT-RAM-2026-10-02-evidencias.json.
- A conclusão do boot ARM64 continua: falhou; última etapa executada desconhecida.

