# Boot ARM64 e TrustZone: referencias proximas ao T7

Data: 2026-10-02. Pesquisa e leitura offline. Nenhum acesso ao roteador, teste, alteracao de bootloader, QSEE, CDT ou flash.

## Conclusao

Existem referencias concretas de boot Linux ARM64 em IPQ5332 e codigo publico de U-Boot AArch32 que faz a passagem por monitor seguro. Nao foi encontrado um bypass comprovado e transferivel da TrustZone Acer. O caminho normal usa a TrustZone; nao a elimina.

## Codigo relevante extraido

Repositorio comunitario 1980490718/u-boot-2016, derivado de QSDK segundo o mantenedor. Commit a67790948d0b6e0fc68e3bebf268b3a6f5c12bba. Nao e o codigo fonte confirmado do U-Boot Acer.

- arch/arm/lib/bootm.c: define cabecalho ARM64, magic 0x644d5241 (bytes ARMd, offset 0x38) e TEST_AARCH64. No caminho 32-bit, boot_jump_linux chama jump_kernel64 se detectar esse magic na entrada do kernel.
- arch/arm/cpu/armv7/qca/common/scm.c: jump_kernel64 monta kernel_params zerado com reg_x0 = endereco do DTB e kernel_start = entrada do kernel. Envia endereco da estrutura e sizeof(param). Verifica a interface SCM e chama SCM_ARCH64_SWITCH_ID/SCM_EL1SWITCH_CMD_ID. Se houver retorno, imprime erro e para.
- scm.h: owner SIP 2, servico 1 e comando 0xf formam 0x0200010f pela macro QCA_SCM_FNID. A chamada usa a instrucao smc #0 no wrapper AArch32. O nome scm_call_64 nao significa que o U-Boot ja execute instrucoes AArch64.

O codigo solicita ao monitor a entrada ARM64; nao fornece o codigo interno da TrustZone nem demonstra como ela programa registradores. Evitar atribuir a RMR_EL3 um mecanismo interno especifico sem firmware/documentacao que o comprove.

Copias locais: fontes/uboot-qsdk-referencia-a67790948d0b (arm-bootm.c, scm.c, scm.h).

## Evidencia Acer conferida nesta pesquisa

Backup: 2 - Backups Originais de Fabrica/appsbl.bin.
SHA-256: 3d6281190512ba50b83eea1a2d6fca69f01da5bb390d52b601e762ce8f1df2fc.

Strings encontradas (offsets em bytes do arquivo, nao enderecos de execucao):

- Jumping to AARCH64 kernel via monitor: 448861.
- Can't boot kernel: 448838.
- Config not available: 408756.

Fato observado: o backup Acer contem mensagens correspondentes ao caminho ARM64 da referencia. Inferencia: ha forte indicio de suporte a esse caminho incorporado. Limite: strings sozinhas nao provam que a funcao e alcancavel no fluxo usado, qual e sua ABI exata ou que a TrustZone Acer aceita o salto. A auditoria do codigo maquina/execucao deve confirmar esses pontos.

Isso reforca que nao se deve partir da premissa de que U-Boot 32-bit torna ARM64 impossivel ou de que substituir QSEE e obrigatorio.

## Placas comparaveis

### GL-BE9300 Flint 3

Mesmo SoC; o port comunitario relata kernel 6.18, boot e SSH funcionando. A instalacao descrita usa o bootloader existente e FIT especifico. Nao demonstra bypass da TrustZone. Diferencas eMMC/Realtek e mapa de reservas impedem transposicao direta da imagem.

Fonte: https://github.com/perceival/openwrt-flint3

### Ubiquiti UniFi U7 Pro XGS

Mesmo IPQ5332. O autor do PR OpenWrt #25185 descreve boot do initramfs pelo bootloader de fabrica. Versoes novas verificam assinatura; o procedimento do autor exige versao anterior do firmware/bootloader daquele aparelho. E uma restricao de autenticacao da imagem relatada para Ubiquiti, nao prova de bloqueio do monitor ARM64 Acer.

Fonte: https://github.com/openwrt/openwrt/pull/25185

### Xiaomi BE6500 RN02

Mesmo IPQ5332, QSDK Linux 5.4.213 de fabrica com ambiente 32-bit e NAND A/B. A fonte consultada relata initramfs ARM64 6.18 compilado/verificado offline, mas boot em hardware ainda nao comprovado no status publicado. Referencia util de metodologia e topologia semelhante, nao caso de sucesso comprovado.

Fonte: https://github.com/pir0c0pter0/xiaomi-be6500-openwrt

## Como isso orienta o T7

Primeiro confirmar offline o fluxo Acer de reconhecimento do Image ARM64, ABI do bloco de parametros, entrada/DTB, descompressao e manutencao de memoria/cache. Manter a TrustZone original. Se possivel obter erro especifico ou checkpoint confiavel da chamada, distinguir rejeicao da imagem, erro retornado pelo SCM e falha posterior do Linux.

Corrigir o diagnostico Ethernet antes de interpretar ausencia de UDP. Um datagrama do init ARM64 e prova positiva de passagem; silencio na rede nao identifica EL3 como causa. A pesquisa nao iniciou teste nem gerou um bypass ou bootloader para instalacao.

Fontes de codigo fixadas:

- https://github.com/1980490718/u-boot-2016/blob/a67790948d0b6e0fc68e3bebf268b3a6f5c12bba/arch/arm/lib/bootm.c
- https://github.com/1980490718/u-boot-2016/blob/a67790948d0b6e0fc68e3bebf268b3a6f5c12bba/arch/arm/cpu/armv7/qca/common/scm.c
- https://github.com/1980490718/u-boot-2016/blob/a67790948d0b6e0fc68e3bebf268b3a6f5c12bba/arch/arm/include/asm/arch-qca-common/scm.h