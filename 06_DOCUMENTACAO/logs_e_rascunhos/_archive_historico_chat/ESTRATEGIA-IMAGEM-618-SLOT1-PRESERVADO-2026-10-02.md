# Estratégia para imagem recente T7 preservando o Slot 1

## Recomendação

Preparar um candidato v3 ARM64 de diagnóstico em RAM a partir da árvore Linux 6.18.52 já existente no projeto, em cópia isolada. Portar seletivamente os corretivos Ethernet identificados e validar antes de acrescentar NAND/UBI e Wi-Fi. Esta é a rota recomendada para aumentar a chance de observar boot e reduzir caminhos de gravação; não é garantia de boot.

Esta etapa apenas definiu a estratégia, leu as evidências existentes e consultou documentação. O v3 não foi compilado, nenhum patch aplicado e nenhum hardware acessado.

## Etapa 1 — FIT de RAM com initramfs mínimo

- Kernel recém-compilado, DTB Acer revisado e initramfs ARM64 no mesmo FIT.
- Mesma versão-base 6.18.52 utilizada pelos candidatos existentes; não declarar automaticamente a mais recente upstream ou um release estável pronto para este aparelho.
- Clocks GCC/NSSCC, interrupções, temporizadores e drivers Ethernet necessários built-in.
- Revisão e portabilidade dos corretivos GL de uso/liberação de skb, DMA RX, limpeza de rings e TX; evitar aplicar séries sobrepostas. Conferir as tabelas IPQ5332 de scheduler/buffers e a topologia Acer.
- CPU secundária mantida fora do primeiro ensaio com maxcpus=1.
- /init estático, identificação exclusiva da compilação, boot_id, release/arquitetura, heartbeat e retransmissão kmsg por UDP.
- Netconsole built-in, sabendo que só funciona após inicialização do dispositivo de rede. Ausência de pacotes continua inconclusiva.
- Sem dependência de NAND, UBI, SquashFS ou overlay. Sem ubi.mtd/root=mtd na cmdline de diagnóstico, usando cmdline forçada própria.
- MTD e caminhos normais de gravação desativados; init sem instalador, sysupgrade ou scripts OEM. PCIe/USB/Wi-Fi e nós de coprocessadores não entram no primeiro ensaio.
- Watchdog tratado pelo driver adequado e keepalive quando disponível. Não assumir que nowatchdog desarma hardware ou que o driver chega a tempo.
- Ramoops compilado só ganha região ativa depois de provar exclusividade e retenção; não usar 0x4cc00000 nem copiar endereços de outra placa.

O candidato v2 existente serve de base de comparação, mas tem defeitos Ethernet identificados ainda sem corretivo aplicado e mantém hardware_ready=false.

## Etapa 2 — verificar entrega OEM antes de qualquer boot

Conferir magic ARMd do payload descompactado, formato real LZMA, configuração FIT compatível com o bootloader Acer, load/entry, CRC/hash, alinhamento e image_size. Validar intervalos de kernel descompactado, FIT de origem, DTB, initramfs e áreas usadas dinamicamente pelo U-Boot. Não reutilizar o endereço antigo que colidia com a descompressão.

Transporte recomendado: TFTP para RAM, acompanhado de acionador temporário compatível com o OEM e comprovadamente limitado a carregar/verificar/iniciar. O mecanismo ainda não está validado sem UART. O TFTP é o transporte, não prova de que Linux iniciou.

Não enviar um FIT comum ao HTTP Failsafe: o handler OEM auditado pode classificá-lo como atualização e gravar flash. O fato de a imagem conter initramfs não torna o upload HTTP seguro. O acionador existente permanece sem liberação até resolver mapa de RAM, fixups/autostart, sintaxe e fluxo do handler.

## Preservação do Slot 1

Na fase RAM, não gravar kernel/RootFS/overlay de nenhum slot, não usar saveenv e não alterar permanentemente seleção de boot ou argumentos OEM. Não atualizar APPSBL/U-Boot, QSEE/TrustZone, SBL, CDT, tabela de partições, ambiente persistente, ART/calibração ou demais regiões compartilhadas. O backup deve permanecer fora do aparelho.

Confirmar o estado do Slot 1 e o retorno à recuperação antes de ensaio. Um reset normalmente encerra o boot temporário em RAM, desde que o acionador e o ambiente persistente não tenham efetuado gravações. Isso depende da validação do caminho OEM; não prometer risco zero ou 100% de certeza.

## Critério de sucesso

Receber no PC a identidade exclusiva do candidato, boot_id válido e uname indicando aarch64 e a release esperada, mais heartbeat ou kmsg. Só link/ping, resposta Acer ou transferência TFTP não bastam. Se nada chegar, não diagnosticar EL3 automaticamente.

## Etapa 3 — OpenWrt completo ainda em RAM

Depois de comprovar kernel e Ethernet, construir initramfs OpenWrt ARM64 com BusyBox, procd, ubus, UCI e SSH, módulos feitos para o mesmo kernel e configuração sem serviços de gravação automática. Ajustar volumes e recursos aos poucos. Wi-Fi/NSS/PPE com desempenho OEM não são requisitos para o primeiro boot comprovado.

## Etapa 4 — imagem persistente exclusivamente para Slot 2

Somente após os boots em RAM: habilitar e validar NAND/QPIC/UBI, construir RootFS OpenWrt correspondente ao kernel e empacotar SquashFS com a receita compatível do projeto. Avaliar os patches NAND segundo o chip real; não reduzir ECC nem truncar IDs genericamente sem justificativa. Revisar WCSS seguro/multipd para Wi-Fi em fase separada com firmware e calibração Acer.

Antes de qualquer gravação, confirmar partição física/label, associação UBI, nome/ID/tipo/tamanho real de cada volume, imagem/capacidade e hashes de backup. Não confiar que ubi1 sempre representa Slot 2. O kernel FIT deve respeitar o volume static observado para o bootipq OEM. O RootFS e seus módulos precisam corresponder à versão/arquitetura do kernel; um clone do RootFS Acer 5.4 não é substituto automático.

Não gravar a imagem NAND completa de outro equipamento. Verificar leituras pós-gravação e ter retorno ao Slot 1 definido; alterar seleção persistente somente dentro de um procedimento separado e revisado. Avisar o usuário antes de testar no hardware.

## Referências

- Candidato atual: DIAGNOSTICO-SEM-UART-REDE-V2-2026-10-02.md.
- Corretivos Ethernet: COMPARACAO-GLINET-T7-2026-10-02.md e IMMORTALWRT-UTILIDADE-T7-2026-10-02.md.
- Série NAND/Wi-Fi: IMMORTALWRT-QUALCOMMAX-REVISAO-AMPLIADA-2026-10-02.md.
- SquashFS: COMPILADOR-OFICIAL-SQUASHFS-T7/v1.0/LEIA-PRIMEIRO.md.
- Boot ARM64: https://docs.kernel.org/arch/arm64/booting.html.
- Initramfs: https://docs.kernel.org/filesystems/ramfs-rootfs-initramfs.html.
- Limites netconsole: https://docs.kernel.org/networking/netconsole.html.
