# Especificação dos artefatos de diagnóstico em RAM — Acer Predator T7

Data: 02/10/2026.
Estado: especificação para revisão, não pronta para execução no hardware.
Autorização desta etapa: leitura e documentação. Nenhum código, configuração ou imagem existente foi alterado. Não houve compilação, geração de ITB, instalação, upload, servidor iniciado ou acesso ao roteador.

## Objetivo e limite

Demonstrar até onde chega o boot ARM64 usando o U-Boot existente, sem escolher ou gravar uma partição de destino.

O objetivo não é instalar OpenWrt nesta etapa. É separar:
1. execução do acionador;
2. transferência e integridade do FIT;
3. tentativa de boot;
4. execução efetiva do kernel e do initramfs.

"Boot pela RAM" descreve a carga e execução; não garante que o script de entrada ou o sistema iniciado deixem a flash intacta. A especificação controla os dois.

## Entregáveis definidos

| Artefato futuro | Função | Conteúdo |
| --- | --- | --- |
| t7-ram-launcher-<build-id>.itb | entrada pelo Failsafe | somente script FIT e padding necessário |
| t7-arm64-diag-<build-id>.itb | imagem recebida por TFTP | kernel ARM64, initramfs mínimo embutido e DTB |
| manifest-<build-id>.json | identidade e validação | hashes, tamanhos, versão, configuração e mapa aprovado |
| registros de sessão | evidência do teste | checkpoints do U-Boot e, se alcançados, identificação/logs Linux |

Nenhum desses nomes representa um binário já produzido. O JSON de especificação associado mantém endereços e hashes executáveis como null, impedindo confundi-lo com um manifesto aprovado.

## Acionador: seleção correta pelo Failsafe

A análise do APPSBL preservado mostrou uma ramificação que escolhe script quando os bytes do upload em 0x5c são "Flas". Nesse caminho, o firmware executa:

sf probe; imgaddr=<endereço do upload> && source $imgaddr:script

O próprio script do acionador não inclui gravação. sf probe é uma operação do handler OEM; não é uma chamada a sf update.

Requisitos do FIT final, não apenas do ITS:
- formato FIT válido, nome de nó script compatível com source $imgaddr:script;
- marcador 466c6173 exatamente em 0x5c;
- nenhum payload de SBL, MIBIB, BOOTCONFIG, QSEE, CDT, APPSBL, UBI ou RootFS persistente;
- padding inerte, não script adicional;
- tamanho máximo planejado de 64 KiB;
- limite mínimo histórico do HTTP a reconfirmar na análise do handler;
- hash do script e do arquivo inteiro recalculados;
- extração independente do script produzido, conferindo texto e comandos.

A descrição começar com "Flash" não é validação suficiente: a posição dos bytes no FIT pode mudar. Se o marcador final não corresponder, bloquear o uso. Um FIT comum de kernel pode seguir uma rotina de gravação no Failsafe.

## Comandos e efeitos permitidos

Lista de operações permitidas no acionador, sujeita a validar a sintaxe OEM:
- atribuições/condições e variáveis voláteis;
- setenv somente para parâmetros da sessão;
- tftpboot para o endereço de RAM aprovado;
- crc32 para um resultado armazenado no buffer aprovado;
- itest/test para comparações de valores definidos;
- mw/cp apenas em faixas explicitamente aprovadas de RAM;
- tftpput para enviar o registro de 64 bytes;
- bootm somente no modo de execução e após todos os critérios passarem;
- saída com retorno de falha.

Proibido no acionador:
- saveenv, fw_setenv e env save;
- flash, flasherase, sf update/write/erase, nand write/erase;
- xtract_n_flash, mibib_reload e imagens de atualização OEM;
- ubiupdatevol, ubiformat, comandos de instalação e mudança de slot;
- escrita em MMIO, QFPROM/fuses ou memória do firmware seguro;
- avaliação de texto recebido da rede como comandos;
- fallback automático para outro arquivo ou firmware.

A revisão deve analisar o script completo, inclusive condições e expansão de variáveis; uma busca textual por palavras proibidas é apenas verificação auxiliar.

Não alterar bootcmd nem persistir ipaddr/serverip. Não chamar bootipq no script como parte de uma tentativa de reparação.

## Máquina de estados

| Estado | Ação | Condição para avançar | Evidência |
| --- | --- | --- | --- |
| S00 | preparar sessão e registro | parâmetros e regiões previamente aprovados | checkpoint S00 |
| S10 | iniciar recepção do FIT | início registrado; autostart controlado | checkpoint S10 |
| S20 | receber e conferir tamanho | retorno TFTP bem-sucedido e tamanho exato | checkpoint S20 |
| S30 | conferir CRC32 | cálculo concluído e valor esperado igual | checkpoint S30 |
| FINAL_CARGA | encerrar modo de ensaio | modo padrão load_and_verify | fim sem bootm |
| S40 | anunciar tentativa de boot | modo de boot, integridade e mapa aprovados | checkpoint S40 |
| BOOT | executar FIT selecionado | chamada explícita após S40 | comprovação Linux separada |
| FAIL | registrar erro e encerrar | qualquer falha anterior | checkpoint FAIL se a rede ainda responder |

O modo padrão é somente carga e verificação. Esse modo não chama bootm, nem mesmo bootm start/loados/prep/fake, pois essas fases podem alterar RAM e hardware.

A presença de subcomandos bootm no binário permite estudar uma sequência explícita, mas o comportamento de autostart e a continuidade da rede entre fases ainda precisam ser revisados. Não gerar comandos de boot até essa revisão.

Uma falha de checkpoint obrigatório deve impedir avançar para bootm: ausência de observabilidade não deve ser tratada como sucesso. O envio de FAIL é tentativa limitada, sem loop de repetição permanente.

Depois que o script retorna, o handler HTTP pode resetar, dependendo do retorno. Não prometer que toda falha deixa o aparelho parado no Failsafe. Bootcmd e slots permanecem sem alteração pelo acionador proposto.

## Integridade antes e depois da transferência

No PC, antes de oferecer arquivos:
- confirmar SHA-256 do acionador e do FIT;
- verificar que o arquivo servido é exatamente o do manifesto;
- recusar nomes alternativos, links de diretório e arquivos desconhecidos;
- validar previamente os limites de tamanho contra o mapa.

No U-Boot:
- verificar retorno de tftpboot;
- confirmar filesize exato, não apenas menor que um limite;
- calcular CRC32 do FIT recebido e comparar com o valor fixado no acionador;
- usar configuração FIT explicitamente identificada.

A sintaxe para guardar o resultado CRC e lê-lo por itest no U-Boot OEM precisa ser validada. Não presumir crc32 -v: o comando encontrado aceita no máximo quatro argumentos e não foi demonstrado suporte a essa opção.

SHA-256 no PC e CRC32 no aparelho controlam identidade/erros de transmissão neste ensaio local; CRC32 não autentica uma origem hostil. O servidor deve oferecer um artefato fixo da sessão, em ligação de teste definida.

Verificar filesize após receber não evita uma sobrescrita já ocorrida. Por isso o servidor precisa rejeitar antecipadamente qualquer arquivo maior que o intervalo aprovado. Também falta concluir o comportamento de limites do receptor TFTP OEM.

## Protocolo de checkpoints

Enviar por tftpput somente um registro inicializado de 64 bytes, little endian, para um nome fixado no manifesto da sessão.

| Offset | Bytes | Campo |
| --- | --- | --- |
| 0x00 | 4 | magic ASCII DGT7 |
| 0x04 | 4 | versão do protocolo, 1 |
| 0x08 | 16 | identificador da sessão |
| 0x18 | 4 | estágio: 0, 10, 20, 30, 40 ou 255 |
| 0x1c | 4 | código de resultado |
| 0x20 | 4 | bytes recebidos |
| 0x24 | 4 | CRC32 calculado |
| 0x28 | 4 | endereço do FIT |
| 0x2c | 4 | tamanho esperado |
| 0x30 | 4 | CRC32 esperado |
| 0x34 | 12 | reservado, preenchido com zero |

Inicializar todo o registro antes do primeiro envio para não exportar bytes anteriores da RAM. Enviar somente esses 64 bytes, não um dump genérico.

Códigos de erro propostos:
- 0: sucesso da etapa;
- 1: falha na transferência;
- 2: tamanho divergente;
- 3: CRC divergente;
- 4: erro de checkpoint;
- 5: parâmetro/estado inválido;
- 6: bootm retornou;
- 7: ensaio de carga encerrado normalmente.

O servidor deve reconhecer a sessão e concluir a transferência antes de considerar um checkpoint recebido. Registrar ordem, horário de chegada no PC, nome e conteúdo validado. UDP perdido não pode ser convertido em prova de travamento.

S40 prova apenas que o acionador chegou antes da chamada de boot. Não prova salto ARM64, execução de start_kernel ou falha EL3.

## Requisitos do servidor TFTP

O servidor existente não é compatível com este plano: ele não trata WRQ e faz fallback de arquivo ausente para openwrt.itb.

Servidor futuro:
- leitura restrita ao FIT fixado e a arquivos explicitamente definidos;
- nenhum fallback;
- suporte WRQ restrito aos nomes de checkpoints da sessão;
- limite de registro recebido de 64 bytes;
- negar nomes/caminhos desconhecidos e tamanho de imagem fora do manifesto;
- timeouts/retransmissões limitados;
- registrar pedido e resultado completo, distinguindo tentativa de transferência de conclusão;
- bind à interface/endereço de teste confirmados.

A especificação não instala nem modifica servidor. O IP histórico do backup e o IP do acionador antigo divergem; a sessão futura terá um único par explicitamente definido.

## Kernel de diagnóstico: impedir os caminhos normais de gravação

A primeira compilação deve ser um kernel de diagnóstico com initramfs, derivado da árvore mainline preservada. Não deve ser o instalador completo do OpenWrt nem reutilizar automaticamente todo root-qualcommbe.

Requisitos de configuração a conferir após resolver dependências:
- CONFIG_MTD=n: não expor NAND/NOR/UBI pelo subsistema MTD;
- CONFIG_MODULES=n: impedir carregar depois módulos de flash;
- CONFIG_DEVMEM=n: não disponibilizar /dev/mem;
- CONFIG_NVMEM_SYSFS=n: não expor interface genérica de escrita NVMEM;
- CONFIG_MMC=n, CONFIG_SCSI=n, CONFIG_USB_STORAGE=n e CONFIG_BLK_DEV_NVME=n;
- CONFIG_PSTORE_BLK=n: diagnóstico não deve usar backend persistente de bloco;
- retirar interfaces e ferramentas de fuse/QFPROM e atualização.

CONFIG_NVMEM inteiro não precisa ser desabilitado se houver dependências de identificação do SoC; avaliar provedores e impedir exposição de caminhos de escrita.

Esses requisitos eliminam caminhos normais de instalação e acesso à flash. Não são garantia matemática contra bugs de kernel, DMA, corrupção de memória ou efeitos de firmware seguro.

Tudo que for indispensável ao boot deve ser built-in, incluindo console, clocks, SCM e eventual suporte de Ethernet da variante observável. Não transplantar módulos OEM de Linux 5.4 para Linux 6.18.

## Initramfs mínimo e identificação de execução

Conteúdo:
- BusyBox mínimo e bibliotecas estritamente necessárias, se não for estático;
- /init próprio, sem o fluxo geral de inicialização/instalação;
- manifesto reduzido de identidade;
- comandos de leitura e diagnóstico.

O /init:
1. monta somente proc, sysfs, devtmpfs e tmpfs;
2. confirma identidade de kernel, arquitetura e sessão;
3. escreve um marcador no log kernel e registra dmesg em tmpfs;
4. abre shell de console ou transporte de leitura autenticado quando houver Ethernet validada;
5. não chama mount_root, switch_root, sysupgrade, firstboot, jffs2reset, fw_setenv ou instalador;
6. não monta volumes persistentes nem inicia serviços OEM;
7. permanece em execução sem reinicialização programada automática.

O preinit padrão OpenWrt tem um gancho mount_root condicionado por INITRAMFS; isso não comprova gravação automática em um boot initramfs correto. Mesmo assim, o primeiro diagnóstico usará /init explícito para tornar o comportamento verificável.

Confirmação de sucesso:
- uname -m informa aarch64;
- uname -r corresponde à compilação;
- sessão/build-id coincidem com o manifesto;
- processo /init de diagnóstico está executando;
- não aparecem dispositivos MTD/UBI nem módulos carregáveis;
- mounts são apenas o rootfs em RAM e os pseudo-filesystems definidos;
- log recebido pertence ao kernel testado.

Responder HTTP/Telnet/SSH isoladamente não é prova: o firmware anterior ou Failsafe também pode responder.

## Configuração básica necessária

Propostos como built-in:
- ARM64, BLK_DEV_INITRD, DEVTMPFS, PROC_FS, SYSFS, TMPFS e PRINTK;
- SERIAL_EARLYCON, SERIAL_MSM e SERIAL_MSM_CONSOLE;
- QCOM_SCM e IPQ_GCC_5332;
- PSTORE, PSTORE_RAM e PSTORE_CONSOLE.

O .config preservado ainda não atende: PSTORE está desabilitado, DEVTMPFS está desabilitado, MTD e MODULES estão habilitados, e INITRAMFS_SOURCE aponta para o root OpenWrt completo. Nenhuma dessas opções foi alterada.

A existência das opções não basta. Conferir .config resolvido, autoconf.h, símbolos pertinentes e os arquivos efetivamente presentes no initramfs do FIT final.

## DTB, bootargs e observabilidade

Requisitos:
- memória real declarada/corrigida, sem assumir 1 GiB a partir de um nome;
- reservas OEM mantidas, inclusive as áreas seguras e de rádio;
- console correspondente à MSM UARTDM em 0x078af000;
- bootargs sem ubi.mtd, root=mtd:ubi_rootfs, rootfstype=squashfs ou rootwait herdados;
- entrada do initramfs explícita;
- nenhuma ativação de NAND/QPIC na variante inicial;
- Wi-Fi, PCIe e serviços de produção fora da primeira tentativa;
- não usar nowatchdog como prova de que o watchdog de hardware foi desativado.

Ramoops precisa de uma região exclusiva e de persistência demonstrada após o reset. Não usar 0x4cc00000, ocupado por m3_dump. O endereço de ramoops continua indefinido; sem ele, não apresentar pstore como diagnóstico validado.

Sem UART e sem Ethernet Linux funcional, os checkpoints apenas observam o U-Boot. Para provar execução do Linux será necessário um canal de retorno do próprio kernel/initramfs ou RAM persistente validada. Isso é um limite real, não uma conclusão de falha EL3.

## Memória: orçamento, não aprovação de endereços

| Uso | Intervalo candidato | Orçamento |
| --- | --- | --- |
| Image com initramfs | [0x41000000, 0x43000000) | 32 MiB |
| acionador HTTP | [0x44000000, 0x44010000) | 64 KiB |
| buffer de registro | [0x45000000, 0x45001000) | 4 KiB |
| FIT TFTP | [0x46000000, 0x47000000) | 16 MiB |

Esses intervalos são somente candidatos do levantamento anterior. O manifesto executável deve continuar sem endereços enquanto não forem confirmados heap, pilha, bancos reais, buffers, destino do DTB e reservas.

A imagem initramfs existente, com image_size=0x03270000, não cabe no orçamento de 32 MiB. Não basta trocar seu endereço no acionador e chamá-la de imagem mínima.

Manter excluído conservadoramente [0x49b00000, 0x55000000). Não utilizar lacunas sem provar sua disponibilidade. fdt_high=0x48500000 é limite superior do backup, não endereço final.

## Critérios de liberação dos testes

Ensaio 1 — carga e verificação:
- revisão independente do FIT acionador produzido;
- marcador de despacho e limite HTTP confirmados;
- faixas de RAM aprovadas para recepção e registro;
- servidor sem fallback, recebimento WRQ validado fora do roteador;
- autostart e sintaxe de comparações OEM revisados;
- modo load_and_verify, sem qualquer bootm.

Ensaio 2 — execução do kernel:
- todos os critérios do ensaio 1;
- mapa de kernel/DTB aprovado e imagem dentro dos orçamentos;
- kernel e initramfs sem caminhos previstos de escrita persistente;
- retorno de diagnóstico definido;
- ensaio 1 concluído com tamanho/CRC corretos;
- autorização específica para reiniciar o aparelho e tentar o boot temporário.

Instalação no Slot 2:
- fora desta especificação;
- depende de comprovar boot, NAND/UBI, rootfs, rede e recuperação;
- exigirá imagem própria e revisão separada de seleção de partição.

## Pendências concretas

1. Confirmar bancos de RAM e ocupação dinâmica do U-Boot. O comando bdinfo existe, mas ainda não há captura desses valores na recuperação.
2. Definir destino real do DTB e comportamento dos fixups.
3. Confirmar a região de diagnóstico e o caminho de retorno Linux.
4. Revisar sintaxe OEM de CRC, comparação, autostart e execução.
5. Validar limite mínimo HTTP e a sequência completa anterior ao despacho.
6. Só então compilar e gerar os dois artefatos, em etapa autorizada.

Não há binário liberado para upload. Este documento transforma o plano em critérios verificáveis e preserva os bloqueios necessários.

## Fontes

- Código/configuração Linux 6.18.52 preservados no WSL e DTS/FITs do projeto.
- Dump APPSBL: SHA-256 3d6281190512ba50b83eea1a2d6fca69f01da5bb390d52b601e762ce8f1df2fc.
- [U-Boot bootm](https://docs.u-boot.org/en/latest/usage/cmd/bootm.html).
- [U-Boot tftpput](https://docs.u-boot.org/en/latest/usage/cmd/tftpput.html).
- [Linux ramoops](https://docs.kernel.org/admin-guide/ramoops.html): exige RAM persistente.
- Complementa os levantamentos anteriores sem modificá-los.

