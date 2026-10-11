# Preparacao offline do diagnostico ARM64

Data: 2026-10-02. Estado: compilacao concluida; candidato sem liberacao para hardware.

O usuario autorizou criar os arquivos necessarios e pediu aviso antes de testar. Nesta etapa foram criadas ferramentas e realizada compilacao local. Nao houve acesso ao roteador, servidor iniciado, upload, reboot, instalacao ou escrita em particoes.

## Fato observado

Foi compilado um kernel novo a partir da arvore Linux 6.18.52 existente no WSL/OpenWrt. Esta e uma arvore local com patches; nao afirmar que equivale a um checkout upstream sem modificacoes.

A compilacao usou uma copia isolada em `/home/builder/t7-chatgpt-work-20261002-v1`. O ExFAT fica com fontes autorais, scripts, logs, evidencias, binarios e um arquivo comprimido das fontes do kernel copiadas. O scratch Linux foi necessario para as operacoes da compilacao e os links da arvore; nao e o local unico dos entregaveis.

| Artefato final | Tamanho |
| --- | ---: |
| Image ARM64 | 10.156.040 bytes |
| image_size do cabecalho ARM64 | 10.485.760 bytes |
| Image.lzma | 3.043.526 bytes |
| FIT candidato | 3.063.368 bytes |
| DTB | 18.775 bytes |
| /init estatico ARM64 | 282.624 bytes |
| initramfs CPIO | 283.648 bytes |

FIT SHA-256: `084c54473930040cc14e0b6790d25bef2f56951e3a5cc24670d54cdbd840302d`.

No mapa candidato, a imagem carregada em 0x41000000 precisaria de espaco ate 0x41a00000. Isso evita a sobreposicao historica com 0x44000000. O mapa dinamico de heap, pilha e buffers do U-Boot ainda nao foi validado; portanto esses enderecos continuam sem aprovacao.

O FIT e candidato para transporte futuro por TFTP. **Nao enviar esse FIT comum ao HTTP Failsafe: o handler OEM pode trata-lo como atualizacao e gravar flash.** Nao foi gerado um acionador ITB de upload.

## Protecoes implementadas no kernel

- PSTORE, PSTORE_RAM, PSTORE_CONSOLE, DEVTMPFS e console MSM compilados como built-in.
- MTD, carregamento de modulos, /dev/mem, NVMEM_SYSFS, MMC, SCSI, PCI e USB desabilitados.
- Provedor QFPROM desabilitado apos auditoria encontrar sua rotina de escrita de fusíveis.
- Drivers de interfaces fisicas de rede desabilitados. O nucleo de rede foi mantido para satisfazer dependencia da arvore local.
- CONFIG_CMDLINE_FORCE=y para impedir que os argumentos OEM de RootFS/UBI substituam a linha de diagnostico.
- /init proprio, estatico, sem shell, sysupgrade, ferramentas de flash, overlay ou scripts OEM.
- Initramfs com exatamente seis entradas: dev, proc, sys, tmp, init e dev/console.

O /init monta somente devtmpfs, proc, sysfs e tmpfs, imprime identificacao e informa a chegada ao espaco de usuario. Se o driver conventional watchdog disponibilizar /dev/watchdog, o /init abre e envia keepalive. Nao ha reboot automatico nem acesso bruto a registradores.

Isso reduz os caminhos normais de gravacao. Nao constitui garantia absoluta contra bugs, DMA, firmware seguro ou efeitos da transicao de arquitetura.

## DTB de diagnostico

- Memoria explicitamente definida como candidato conservador de 512 MiB, evitando reg de tamanho zero. O tamanho real e os fixups do OEM continuam pendentes.
- Reservas herdadas de U-Boot/SBL/TZ/SMEM e reservas adicionais conservadoras cobrem 0x49b00000 a 0x55000000.
- UART MSM UARTDM em 0x78af000, sem presumir GENI em 0xa84000.
- Bootargs sem ubi.mtd, root=mtd, rootfstype=squashfs ou rootwait.
- PCIe e PPE desativados nesta etapa.
- Watchdog mantido com driver padrao; seu funcionamento precoce nao foi demonstrado.
- Ramoops sem regiao no DTB. Embora o driver esteja compilado, ainda nao ha area habilitada para registrar logs persistentes. Nao reutilizar 0x4cc00000.

## Verificacoes locais

A verificacao independente do FIT confirmou que o payload e LZMA real e descompacta exatamente para a Image nova. Conferiu ARMd, alinhamento, image_size, configuracao config@mi01.6, DTB, initramfs e /init ELF64 estatico.

Os simbolos ramoops_probe e pstore_register estao presentes no novo vmlinux.

O verificador textual estrito ainda sinalizou USB_STORAGE e BLK_DEV_NVME ausentes. A verificacao do Kconfig explicou esses casos: os pais SCSI/USB e PCI estao desativados, respectivamente. Isso e diferente das divergencias explicitas da configuracao original.

O protocolo TFTP passou oito testes locais com sockets simulados: sessao, tamanho, CRC, preenchimento, caminho, modo, ACK perdido, bloco final e registro excessivo. Nenhum socket de rede foi aberto nesses testes. O servidor real ainda nao foi ensaiado contra o OEM.

O SHA-256 da configuracao original antes/depois permanece:
`2e14935e4f2a3cc872b5934f2b4ad0abd525a93fbd13b1322d148de12f2d88c8`.

## Ferramentas criadas

- compilar_diagnostico.sh: cria scratch separado, compila kernel/init, DTB e FIT candidato; recusa reutilizar diretorios existentes.
- empacotar_candidato.py: gera FIT e manifesto com hardware_ready=false.
- verificar_artefatos.py: confere FIT, Image, configuracao, initramfs e init.
- tftp_restrito.py: servidor futuro com arquivo fixo, sem fallback, peer definido, checkpoints de 64 bytes e logs de conclusao.
- verificar_protocolo_local.py: testes sem rede.
- gerar_acionador_verificacao.py: gerador bloqueado sem validacoes de RAM, sintaxe OEM e handler. Esta versao gera somente load_and_verify, sem bootm.

Os scripts retomar_compilacao_* preservam o historico dos reparos da compilacao. O procedimento principal atualizado esta em compilar_diagnostico.sh.

## O que ainda impede o teste

1. Mapa dinamico do U-Boot e limites de recepcao TFTP.
2. Posicionamento/fixups do DTB e comportamento OEM de autostart e CRC32.
3. Validacao do acionador no handler HTTP.
4. Caminho para observar o Linux: UART ou outra saida comprovada. Checkpoints TFTP do U-Boot nao substituem console Linux.
5. Regiao exclusiva e retencao apos reset antes de ativar ramoops.

Os manifestos permanecem bloqueados. Nao ha evidencia nova de barreira EL3, nem comprovacao de boot ARM64 neste aparelho.

## Fontes e evidencias

- [Manifesto final](artefatos/t7-diag-20261002-v1/manifesto-candidato.json)
- [Verificacao offline](artefatos/t7-diag-20261002-v1/verificacao-offline.json)
- [Configuracao final](artefatos/t7-diag-20261002-v1/kernel.config)
- [Log final de compilacao](logs/compilacao-20261002-v1-sem-qfprom.log)
- [Testes locais do protocolo](logs/verificacao-protocolo-local.txt)
- [Boot ARM64: cabecalho, alinhamento e memoria](https://docs.kernel.org/arch/arm64/booting.html)
- [Initramfs e execucao de /init](https://docs.kernel.org/filesystems/ramfs-rootfs-initramfs.html)
