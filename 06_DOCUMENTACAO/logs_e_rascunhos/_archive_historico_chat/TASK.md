# Andamento — diagnostico pela RAM

## Autorizacao atual

Usuario: "pode criar tudo que for preciso e antes de testar me avisa".
Preparacao e compilacao offline autorizadas. Parar e avisar antes de qualquer teste no roteador.
Nao houve acesso remoto, upload, instalacao, servidor de rede iniciado ou reboot.

## Concluido

- [x] Pasta propria e copias dos relatorios anteriores com hashes conferidos.
- [x] Fontes do init minimo e DTB candidato.
- [x] Compilacao nova em copia isolada da arvore Linux 6.18.52.
- [x] Kernel com PSTORE/ramoops e sem MTD, modulos, /dev/mem e QFPROM.
- [x] FIT com LZMA real, initramfs minimo e manifesto bloqueado.
- [x] Arquivo comprimido das fontes copiadas e logs preservados.
- [x] Verificacao independente de FIT, Image, DTB, config e initramfs.
- [x] Oito testes locais de protocolo com sockets simulados.
- [x] Servidor TFTP restrito criado, sem iniciar.
- [x] Gerador de acionador somente load_and_verify, bloqueado pelos requisitos pendentes.
- [x] Configuracao original conferida intacta antes/depois.

## Pendente antes de hardware

- [ ] Confirmar bancos de RAM, heap, pilha e buffers dinamicos do U-Boot.
- [ ] Confirmar posicao e fixups do DTB durante bootm.
- [ ] Confirmar sintaxe OEM de CRC32 e comportamento de autostart/TFTP.
- [ ] Validar handler HTTP e marcador Flas no futuro acionador final.
- [ ] Definir retorno observavel do Linux: UART ou alternativa validada.
- [ ] Confirmar regiao exclusiva e retencao para ativar ramoops.
- [ ] Avisar usuario antes de iniciar qualquer teste no aparelho.

## Limite tecnico atual

Manifestos com hardware_ready=false e upload_authorized=false.
FIT comum nao deve ser enviado ao HTTP Failsafe.
Nenhum acionador ITB de upload foi gerado.


## Atualizacao: evitar UART — variante Ethernet v2

- [x] Drivers PPE/EDMA, PCS, MDIO e QCA808x incluidos como built-in.
- [x] Netconsole direcionado a lan, conforme nome definido pelo driver/DTS.
- [x] Init estatico com identidade de compilacao, boot_id, arquitetura, release e envio kmsg por UDP.
- [x] Coletor e quatro testes locais de parser sem rede.
- [x] Compilacao v2 e verificacao independente concluidas.
- [x] Protecoes de flash mantidas e v1 preservada.
- [ ] Funcionamento Ethernet/netconsole no aparelho ainda nao comprovado.

Nao houve acesso ao roteador ou captura de rede iniciada. Ainda avisar antes de testar. Sem pacote Linux, o diagnostico continua inconclusivo.

## Atualizacao: extracao e comparacao GL.iNet IPQ5332

- [x] 223 fontes extraidas de commit fixo, Git blob e SHA-256 conferidos.
- [x] Diffs por caminho, renumeracao e DTS Acer-versus-GL preservados.
- [x] Comparacao contra fontes efetivamente usadas no candidato v2.
- [x] Identificado defeito RX presente; corretivo remoto 0410 ainda nao aplicado.
- [x] Registradas diferencas TX, scheduler/buffers, clocks, NAND, FIT e ramoops.
- [x] .config original e FIT v2 preservados, hashes conferidos.
- [ ] Futuro v3 exige portabilidade seletiva, recompilacao e verificacao offline.
- [ ] Manter requisitos pendentes e aviso antes de qualquer teste no aparelho.

Relatorio: COMPARACAO-GLINET-T7-2026-10-02.md. Nenhum firmware instalado ou teste iniciado.

## ImmortalWrt — levantamento offline

- [x] Conferidas master, 24.10 e 25.12 em commits fixos: sem perfil T7/ipq53xx encontrado.
- [x] Corretivo DMA RX extraido e comparado com fonte do candidato e patches GL 0420/0421.
- [x] SCM PAS/MSA identificado como suporte de coprocessador, nao transicao CPU ARM64.
- [ ] Revisar sobreposicao dos corretivos no futuro v3; nenhum aplicado nesta etapa.

Relatorio: IMMORTALWRT-UTILIDADE-T7-2026-10-02.md. Nenhum teste no roteador.


## Boot ARM64 / TrustZone — referencias

- [x] Extraidas fontes publicas QSDK bootm/scm em commit fixo.
- [x] Conferidas mensagens de passagem ARM64 no backup APPSBL Acer.
- [x] Separados casos Flint, U7 Pro XGS e Xiaomi RN02 e limites das evidencias.
- [ ] Confirmar fluxo/ABI no codigo maquina Acer; nenhum bypass comprovado.

Relatorio: BOOT-ARM64-TRUSTZONE-REFERENCIAS-2026-10-02.md. Nenhum teste no aparelho.

## mksquashfs compatível — levantamento e validação offline

- [x] Localizadas duas revisões históricas; layout Netgear mais antigo descartado como correspondência Acer.
- [x] Compilados mksquashfs/unsquashfs 4.2 com patches OpenWrt v17.01.0 em scratch isolado.
- [x] Extraído somente etc/version do backup Acer; conteúdo 1.01.000024.
- [x] Gerada imagem sintética; opções XZ 12 bytes idênticas ao backup; round-trip do arquivo passou.
- [x] Salvos binários, fontes, hashes, logs e scripts na pasta própria.
- [ ] Executável/toolchain exato Acer não identificado; montagem OEM e RootFS completo ainda não validados.
- [ ] Avisar antes de qualquer teste no roteador.

Relatório: MKSQUASHFS-COMPATIVEL-ACER-2026-10-02.md. Nenhuma gravação ou teste no aparelho.

## Teste completo SquashFS — offline

- [x] Extraído todo o RootFS original, remontado em saída nova com -noappend e extraído novamente.
- [x] Conferidos SHA-256 individuais de 4.303 arquivos, caminhos, modos, donos, destinos de 473 links e dispositivo.
- [x] Opções XZ 12 bytes iguais; imagem 39.595.738 bytes cabe na referência histórica de 39.870.464 bytes.
- [x] Backup original preservado, hash antes/depois igual.
- [x] Identificada limitação do extrator: mtime dos 473 symlinks não restaurado; resultado bruto differences preservado.
- [ ] Restauração de timestamps de symlinks necessária para round-trip estrito completo.
- [ ] Montagem OEM e boot não testados; capacidade atual do volume não consultada.

Relatório: TESTE-SQUASHFS-COMPLETO-2026-10-02.md. Nenhuma ação no roteador.

## Correção de mtime de symlinks — concluída offline

- [x] Corrigido unsquashfs em scratch v3 com utimensat/AT_SYMLINK_NOFOLLOW, preservando ferramentas anteriores.
- [x] Recompilado extrator; mksquashfs permaneceu com o mesmo SHA-256.
- [x] Repetida extração/remontagem/extração completa: status passed, zero diferenças inclusive nos 473 symlinks.
- [x] Imagem nova: 39.595.654 bytes; margem histórica 274.810 bytes; original intacto.
- [x] Salvos patch, fontes, binários, hashes, logs, resultados e relatório.
- [ ] Montagem OEM/boot não testados; aviso antes de qualquer teste no aparelho continua necessário.

Relatório: CORRECAO-SYMLINK-MTIME-TESTE-2026-10-02.md. A limitação de datas do relatório anterior foi resolvida na nova ferramenta e no novo teste, sem apagar o histórico.

## Pacote canônico do compilador SquashFS T7 — v1.0

- [x] Criada pasta COMPILADOR-OFICIAL-SQUASHFS-T7/v1.0 com binários, fontes, patches, evidências e licença.
- [x] Documentada referência oficial interna; sem atribuir homologação Acer ou compilação de kernel.
- [x] Criados procedimentos parametrizados de compilação e round-trip e contexto para outra IA.
- [x] Recompilação da receita do pacote conferida: hashes iguais aos binários que passaram no round-trip completo.
- [x] Sintaxe/CLI dos scripts conferidos; SHA256SUMS de todos os arquivos passou; ZIP verificado contra arquivos locais.
- [x] Criado ZIP de 434.179 bytes, sem firmware, árvores extraídas ou configurações privadas.
- [x] Histórico e artefatos anteriores preservados; índice README atualizado.
- [ ] Montagem pelo kernel OEM e boot continuam não comprovados; avisar antes de teste no aparelho.

Entrada: COMPILADOR-OFICIAL-SQUASHFS-T7/v1.0/LEIA-PRIMEIRO.md.
ZIP SHA-256: 5c9b6f08fade66a5522bae84cb4e37119e67b33f3419913f5856a97058bcde1f.

## Comparação com MD5 do volume original informado

- [x] Backup local MD5 022605865983843c69395859b9ee7e64 coincide com o relato do usuário.
- [x] Imagem gerada MD5 d19a150765e7c7d6599f2aceb1a07299: equivalência de conteúdo validada, identidade binária não.
- [x] Conferidos timestamps de construção, offsets, bytes_used, hashes de payload e preenchimento 0x00/0xff em memória.
- [x] Documentado que igualdade de conteúdo não implica igualdade binária nem boot; hashes diferentes não demonstram panic.
- [x] Pacote v1.0 preservado; comparação e relatório complementar salvos.
- [ ] Estado do Slot 2, overlay, bootargs e boot relatados não verificados no aparelho nesta etapa.

Relatório: IDENTIDADE-BINARIA-SQUASHFS-2026-10-02.md. Nenhum acesso ao roteador.

## ImmortalWrt qualcommax — revisão ampliada

- [x] Extraídos os 93 patches do commit fixo; Git blobs/SHA-256 conferidos (728.419 bytes).
- [x] Revisados WCSS seguro/Q6 multipd com suporte IPQ5332, NAND/QPIC e combo PHY.
- [x] Identificados cuidados: 0911 usa r_len não inicializado; 0411/0412 truncam IDs globalmente; PSCI 0903 é IPQ6018.
- [x] Conferidas fontes locais e hashes originais; nenhum patch aplicado ou kernel compilado.
- [x] Documentada prioridade RAM/Ethernet, depois NAND/UBI, depois Wi-Fi.
- [ ] Compatibilidade real com firmware, NAND e topologia Acer não comprovada.

Relatório: IMMORTALWRT-QUALCOMMAX-REVISAO-AMPLIADA-2026-10-02.md. Nenhuma ação no roteador.

## Estratégia de imagem recente preservando Slot 1

- [x] Documentada sequência: v3 diagnóstico em RAM com corretivos Ethernet, OpenWrt initramfs completo, depois Slot 2.
- [x] Explicitadas proteções de partições compartilhadas e risco do FIT comum no HTTP Failsafe.
- [x] Definidos critério de sucesso e pendências de acionador/mapa RAM/recuperação.
- [ ] v3 ainda não compilado; patches ainda não aplicados; teste hardware exige aviso prévio.

Relatório: ESTRATEGIA-IMAGEM-618-SLOT1-PRESERVADO-2026-10-02.md. Nenhuma ação no aparelho.

## Preparação do teste em RAM v3 — concluída offline

- [x] Aplicados sete corretivos Ethernet na cópia isolada, com dry-run e sem fuzz.
- [x] Recompilado Linux 6.18.52 ARM64 com initramfs de diagnóstico, MTD e remoteproc desativados.
- [x] FIT de 3.503.744 bytes validado; config, DTB, ELF, fontes e hashes preservados.
- [x] Sonda OEM de comunicação separada preparada; sem download de kernel, bootm ou saveenv.
- [x] Dezesseis verificações locais passaram; logs e preflight PC preservados.
- [x] Ethernet 4 UP no último preflight; IP informado 192.168.73.2, slot atual ainda não comprovado.
- [x] Roteiro e critérios de identidade/sucesso documentados em PREPARACAO-TESTE-RAM-V3-2026-10-02.md.
- [ ] Confirmar slot, recuperação e caminho OEM antes de liberar sonda no hardware; aviso prévio obrigatório.
- [ ] Validar mapa RAM dinâmico, fixups, CRC e carregamento antes de gerar acionador de boot.
- [ ] Nenhuma imagem enviada, listener iniciado, configuração de PC alterada ou instalação realizada.

Esta etapa supera a anotação histórica de v3 ainda não compilado. hardware_ready permanece false.

## Restaurador Slot 1 fornecido — validado offline

- [x] FIT, CRCs e payload bootconfig iguais aos backups originais.
- [x] Cópia preservada e script extraído; relatório VALIDACAO-RESTAURADOR-SLOT1-2026-10-02.md.
- [x] Identificados saveenv e erase/write das duas cópias de bootconfig, sem controles de erro.
- [ ] Não comprovado no aparelho atual; nenhum upload ou execução.

## Conferência real do Slot 2 — somente leitura

- [x] Slot 1 ativo confirmado por bootargs/MTD/UBI/mount.
- [x] Varredura de 960 cabeçalhos da mtd20 sem ubiattach; duas tabelas válidas e coerentes.
- [x] SHA-256 kernel, RootFS e wifi_fw do Slot 2 iguais ao Slot 1.
- [x] Volume rootfs_data reservado, sem blocos associados: compatível com overlay vazio.
- [x] Relatório CONFERENCIA-SLOT2-ATUAL-2026-10-02.md e evidências preservados.
- [ ] Boot Slot 2 não testado; nenhuma restauração/regravação necessária demonstrada.


## Retorno Slot 1 — preparação atual de 03/10/2026

- [x] Capturados backups atuais somente leitura: BOOTCONFIG, BOOTCONFIG1, APPSBLENV e exportações proc.
- [x] Confirmado CRC APPSBLENV com estrutura de 256 KiB dentro da partição de 512 KiB.
- [x] Candidato FIT de retorno gerado e conferido offline, com comparações antes/depois das escritas propostas.
- [x] Trinta simulações de fluxo aprovadas; testes não validam comandos/hush/hardware reais.
- [x] Detectada diferença 0x04 entre flash (2) e exportação proc (3); evidência preservada.
- [x] Relatório RETORNO-SLOT1-PREPARADO-2026-10-03.md e manifestos salvos.
- [ ] Validar geração/seleção das BOOTCONFIG, execução HTTP e mapa RAM antes de liberar recuperação.
- [ ] Boot Slot 2 ainda não testado; nenhum chaveamento, upload, flash ou reboot nesta etapa.

Atualização do histórico: uma sonda de comunicação sem gravação persistente já foi enviada pelo usuário em etapa anterior, sem retorno esperado. Houve consultas remotas somente leitura. Não houve teste do kernel v3. As anotações antigas de nenhum acesso/teste descrevem apenas suas respectivas etapas.
