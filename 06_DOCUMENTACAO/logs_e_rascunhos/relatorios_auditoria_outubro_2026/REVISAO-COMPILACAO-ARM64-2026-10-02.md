# Revisão da compilação ARM64 do Acer Predator Connect T7

Data: 02/10/2026. Escopo: revisão estática, sem instalação, recompilação, execução dos scripts de teste ou acesso ao roteador.

## Conclusão

Há defeitos confirmados na instrumentação de diagnóstico e no empacotamento, além de dependências de boot não demonstradas. A ausência de printk no dump preservado não comprova que o Linux deixou de executar, nem identifica uma falha SMC/EL3.

O achado principal é que a configuração disponível desabilita PSTORE. Os scripts que produzem os FITs denominados "ramoops" e "618-final" reutilizam o mesmo kernel comprimido e somente alteram o DTB/descritor FIT: não compilam suporte ramoops no kernel. A presença de um nó ramoops no DTB não implementa o driver.

Nenhuma correção foi aplicada. Os únicos arquivos criados nesta revisão são este relatório e o manifesto JSON de evidências. TASK.md e documentos históricos não foram alterados.

## Material examinado

- Workspace: H:\FEITOS COM IA\Acer-Predator-Connect-T7.
- Build WSL: /home/builder/openwrt, distribuição Ubuntu.
- Commit do build: 4daa3c165b5449dec86c2e9b134b62c5c5d6d86a.
- Revisão declarada: r36351-4daa3c165b; kernel 6.18.52.
- Configuração real: build_dir/target-aarch64_cortex-a53_musl/linux-qualcommbe_ipq53xx/linux-6.18.52/.config.
- Cabeçalho gerado autoconf.h, ELFs preservados, Image/Image-initramfs, ITS e DTBs.
- Quatro FITs kernel, dois ITBs, sysupgrade.bin e dois SquashFS preservados.
- Scripts de geração, teste e extração de diagnóstico; lidos como texto, nunca executados.
- Dump ramoops_raw.bin, relatório textual associado e DTS OEM.
- Os scripts de recuperação não foram executados nem foi aberto serviço HTTP/TFTP.

## Achados prioritários

### 1. P1 — Instrumentação ramoops sem suporte compilado

Evidências:

- .config, linha 5073: "# CONFIG_PSTORE is not set".
- .config, linha 1909: "# CONFIG_NETCONSOLE is not set".
- autoconf.h não define suporte PSTORE.
- nm dos quatro ELFs vmlinux, vmlinux.debug, vmlinux-initramfs e vmlinux-initramfs.debug não encontra ramoops_probe, pstore_register, pstore_init ou persistent_ram_new.
- build_kernel_ramoops_fit.py, linhas 36–37 e 147–150, extrai e reempacota kernel existente.
- preparar_kernel_618_perfeito.py, linhas 28–29 e 132–133, faz o mesmo.
- Os quatro FITs kernel contêm o mesmo payload comprimido: SHA-256 03b50a02ebe639f81a8c3b08a77f36960bc8ed7c72169e72c0605c6e27a8467e.
- Payload descomprimido: 15.046.664 bytes; SHA-256 0b059663b8499c170e113a2ca78b2804154f01270c5ed35dee81666787a34a13.

Impacto: o ensaio apresentado como "kernel com ramoops" não habilitou ramoops por recompilação. O nó DTB sozinho não poderia produzir o console persistente esperado.

Limite: IKCONFIG também está desabilitado; não existe configuração embutida para extração independente do FIT. A combinação do build, ELFs e scripts sustenta o achado, mas não foi lida a imagem atualmente instalada.

Recomendação futura, não aplicada: suporte PSTORE/PSTORE_RAM/PSTORE_CONSOLE integrado ao kernel e verificação do backend, antes de usar a ausência de logs como indicador de execução.

### 2. P1 — Ramoops e m3_dump sobrepostos no DTB

Os FITs kernel-ramoops e kernel-618-final contêm simultaneamente:

- /reserved-memory/ramoops@4cc00000: reg = <0 0x4cc00000 0 0x100000>.
- /reserved-memory/m3_dump@4cc00000: reg idêntico, com no-map.

É uma sobreposição exata de 1 MiB. Os scripts apenas inserem o novo nó e mantêm a reserva OEM.

Impacto: a área não é uma reserva exclusiva para ramoops; pode ter outro proprietário/atributos. Não se demonstrou que firmware, kernel de recuperação e bootloader preservam o conteúdo.

Recomendação futura: escolher área realmente livre e reservada em todas as etapas pertinentes, com teste controlado de retenção. Não reutilizar área de dump Qualcomm por suposição.

### 3. P1 — DTBs descrevem RAM com tamanho zero

Todos os DTBs mainline examinados têm:

memory@40000000/reg = 00000000400000000000000000000000

Isso significa base 0x40000000 e tamanho zero. O ipq5332.dtsi do build, linhas 101–105, comenta explicitamente que o bootloader deve preencher o tamanho.

O DTS OEM extraído do Linux descreve 1 GiB, mas isso não prova que o U-Boot preencherá o nó do DTB mainline, cujo formato/caminho pode diferir do OEM.

Impacto condicional: se o fixup não ocorrer antes de entrar no Linux, o kernel não recebe RAM utilizável nesse nó e pode falhar muito cedo. É uma hipótese alternativa à barreira de arquitetura.

Recomendação futura: verificar o DTB efetivamente entregue ao kernel. Não declarar o tamanho zero como causa confirmada sem essa verificação.

### 4. P1 — DTBs não descrevem a NAND usada pelo rootfs

A inspeção das propriedades compatible dos DTBs mainline não encontrou nós NAND/QPIC. O DTS do T7 habilita UART, Ethernet e PCIe, mas não adiciona/habilita o controlador SPI NAND OEM em 0x079b0000.

O kernel tem drivers MTD/UBI, CONFIG_MTD_NAND_QCOM=y e CONFIG_SPI_QPIC_SNAND=y, porém o driver precisa de um dispositivo descrito/instanciado.

Impacto: o kernel sem initramfs depende da NAND/UBI para chegar ao userspace. Ter o SquashFS correto gravado não basta se o controlador e as partições não aparecerem no Linux.

Limite: não se capturou o DTB pós-fixup nem se demonstrou injeção de nó NAND pelo U-Boot. O achado é confirmado nos artefatos em disco.

### 5. P1 — FIT final aponta para outra partição UBI

- kernel-arm64 e kernel-ramoops: ubi.mtd=rootfs_1.
- kernel-618-final: ubi.mtd=rootfs.
- preparar_kernel_618_perfeito.py, linhas 41–46, muda explicitamente o argumento para rootfs.
- O mapa OEM identifica rootfs_1 como mtd20/Slot 2 e rootfs como mtd21/Slot 1.

Impacto condicional: se esses argumentos chegarem ao Linux sem alteração, o FIT final tenta anexar o UBI da partição diferente daquela usada nos ensaios do Slot 2. Isso pode montar o rootfs Acer/arquitetura incorreta ou simplesmente falhar.

O U-Boot pode sobrescrever bootargs; não foi provado que isso ocorreu. É necessário registrar a linha de comando efetiva.

### 6. P1 — openwrt_live_boot.itb contém FIT onde declara LZMA

No nó /images/kernel@1:

- compression = lzma.
- Os dados começam por d00dfeed: são outro FIT, não um stream LZMA.
- O payload tem 13.238.272 bytes e corresponde ao ITB initramfs inteiro.
- A tentativa de descompressão LZMA somente em memória falha: "Input format not supported by decoder".
- O script embutido chama bootm 0x44000000#config@mi01.6; não extrai o FIT interno.

Impacto: esse artefato histórico não é um teste válido de entrada no kernel: seu empacotamento pode falhar antes da transferência de controle.

Escopo: não confundir esse defeito com os FITs kernel-618-final/ramoops, cujos streams LZMA e hashes foram validados.

### 7. P1 — Imagem initramfs pode sobrepor a origem da descompressão

O initramfs ITB usa load/entry 0x41000000; image_size no cabeçalho ARM64 é 0x03270000.

A região necessária é [0x41000000, 0x44270000). Se o FIT for carregado em 0x44000000 como nos procedimentos anteriores, a região de destino intersecta o FIT de origem.

Impacto condicional: o U-Boot precisa tratar essa sobreposição corretamente por cópia/relocação/proteção. Não há log demonstrando essa gestão. Isso é uma alternativa concreta a investigar nos testes initramfs.

Os kernels sem initramfs terminam em 0x41eb0000 nesse endereço de carga e não apresentam essa mesma sobreposição com 0x44000000.

## Outros achados

### 8. P2 — Endereço do primeiro FIT viola o alinhamento do cabeçalho

openwrt-predator-t7-kernel.fit usa load/entry 0x40008000; o Image nele tem text_offset=0. A base resultante não é alinhada a 2 MiB, contrariando o protocolo ARM64.

Nos FITs arm64/ramoops/final, load/entry 0x41000000 satisfaz o alinhamento. Portanto esse defeito se aplica ao primeiro FIT, não explica sozinho o teste final.

### 9. P2 — nowatchdog não comprova watchdog físico desligado

CONFIG_QCOM_WDT=y, e o nó watchdog@b017000 continua presente nos DTBs.

O parâmetro nowatchdog é tratado em kernel/watchdog.c, linhas 379–384, alterando watchdog_user_enabled dos detectores de lockup. Ele não equivale a uma escrita no registrador de desabilitação do watchdog Qualcomm.

Impacto: pode haver reset por watchdog físico mesmo com nowatchdog na linha de comando. O estado do hardware e a causa de reset não foram lidos nesta revisão.

### 10. P2 — sysupgrade gerado sem suporte de instalação T7

- target/linux/qualcommbe/ipq53xx/base-files/lib/upgrade/platform.sh aceita apenas ubnt,u7-pro-xgs.
- Acer T7 cai no erro "Sysupgrade is not supported on your board yet".
- O membro kernel do tar sysupgrade é LZMA cru, de 4.519.081 bytes, não FIT.
- O perfil T7 usa KERNEL := kernel-bin | lzma, sem o estágio FIT para esse artefato.

Impacto: a existência de sysupgrade.bin não demonstra um pacote instalável no layout OEM. Não gravar o membro kernel diretamente esperando que ele seja um FIT para bootipq.

### 11. P2 — Ethernet e monitoramento não comprovam execução/arquitetura

- CONFIG_QCOM_PPE=m e CONFIG_PCS_QCOM_IPQ9574=m.
- NETCONSOLE está desabilitado.
- O DTB tem MACs locais zerados e não inclui modelo completo do switch QCA8384; o nó LAN não descreve o switch externo.
- test_route2_arm64_boot.py, linhas 82–97, declara sucesso ARM64 ao encontrar qualquer porta HTTP/SSH/Telnet em três IPs, sem consultar uname, slot ou rootfs montado.
- O IP 192.168.1.1 também pode corresponder ao failsafe.

Impacto: ausência de rede não prova ausência de execução do Linux; porta aberta não prova boot ARM64. Falta a identificação do sistema que respondeu.

A calibração ART usa o mesmo offset 0x58800/0x2d000 do Ubiquiti no hotplug. Não foi demonstrado nesta revisão que esses offsets e BDF são corretos para os rádios do T7. Tratar como pendência, não como defeito comprovado.

### 12. P2 — Dump e scripts não fornecem a prova atribuída a eles

ramoops_raw.bin tem 1.048.576 bytes, SHA-256 86a13075e6730c536628b2f5a4e3e7d0aefd444664833956705ae86859ba7e48.

Contagem de bytes:

- 0x00: 524.286.
- 0xff: 524.282.
- 0xbf: 3; 0x04: 2; 0xfd/0xfe/0xdf: 1 cada.

Há alternância regular de blocos de 128 bytes 0xff/0x00, com poucas exceções. Não é um buffer de texto Linux identificável; a origem desse padrão não foi determinada.

extrair_ramoops_log.py, linhas 150–182, rotula qualquer conteúdo não totalmente zero/ff e sem marcador como sucesso por sobrescrita. Isso não identifica quem escreveu. O dump é obtido depois de iniciar outro firmware, sujeito a sobrescrita.

executar_teste_618_estatico.py e executar_teste_618_completo.py imprimem sucesso após enviar comandos, sem verificar sistematicamente status de saída de ubiupdatevol ou fazer leitura de retorno dos bytes gravados. O primeiro também espera uma string que aparece no próprio comando enviado por Telnet, podendo confundir eco com execução concluída.

Esses scripts foram apenas lidos. Não foi testada sua execução.

### 13. P2 — Fontes e artefatos não representam uma única revisão

- DTS arquivado em "5 - Codigo Fonte e DTS" tem SHA-256 ab5b70c61c56877673c5d6f1b0040b8d6b98bcce871a77c273028a5dfd8f78ab.
- DTS corrente no WSL tem SHA-256 71418492a5893fa9ba7a69a68f77d0823498f1a6485f3d11db5506baa3de25e0.
- O DTS arquivado não inclui bootargs/reservas posteriores.
- Image do build tem SHA-256 18f86dca1e08af144177d82d39d2de46113ab3ce19591c158339973b572a6867.
- O kernel dos FITs difere desse Image em 43 bytes; o cabeçalho ARM64 é igual. Os offsets observados ficam em áreas de notas/metadados; essa diferença não foi atribuída como causa do bootloop.
- root.squashfs e o membro root do sysupgrade têm hashes diferentes, mas ambos declaram OpenWrt r36351-4daa3c165b e o root standalone contém módulos 6.18.52.

Impacto: antes de relacionar uma configuração a um teste, identificar o artefato por SHA-256. Nomes como final/perfeito/ramoops não são evidência de capacidades compiladas.

## Verificações que passaram

- CRC32 e SHA1 dos nós de kernel e DTB dos FITs examinados conferem, inclusive no FIT live cujo empacotamento é incorreto.
- FITs kernel-arm64, kernel-ramoops e kernel-618-final descomprimem em memória sem erro.
- Magic ARM64 ARMd está presente; text_offset=0, flags=0xa e image_size=0xeb0000 nos kernels sem initramfs.
- 0x41000000 cumpre alinhamento do protocolo e a região do kernel sem initramfs não intersecta as reservas TrustZone listadas.
- CONFIG_IPQ_GCC_5332=y, CONFIG_QCOM_SCM=y, CONFIG_SERIAL_MSM=y e CONFIG_SERIAL_MSM_CONSOLE=y.
- UARTDM em 0x078af000 está habilitada; os FITs ramoops/final usam earlycon=msm_serial_dm,0x078af000.
- A presença dos drivers GCC/SCM não comprova funcionamento no hardware; tampouco sustenta que esses drivers estejam ausentes.

## Limites e sequência recomendada, sem execução

1. Preservar a conclusão atual como "boot ARM64 falhou; última etapa executada desconhecida".
2. Em trabalho futuro autorizado, corrigir/verificar RAM, NAND, partição de rootfs e instrumentação de logs.
3. Separar um diagnóstico mínimo em RAM do suporte completo Ethernet/Wi-Fi e do instalador OEM.
4. Verificar retenção de memória e obter uma evidência de entrada no kernel antes de atribuir causa ao QSEE.
5. Se necessário, UART pode resolver a observabilidade; a auditoria não demonstrou que substituir U-Boot/QSEE seja necessário.

Não houve teste de boot, acesso de rede ao T7, alteração de slot, gravação UBI/MTD, atualização de firmware ou compilação nesta revisão.

## Referências técnicas

- [Protocolo de boot ARM64](https://docs.kernel.org/arch/arm64/booting.html).
- [Ramoops e requisito de RAM persistente](https://docs.kernel.org/admin-guide/ramoops.html).
- [Parâmetros do kernel](https://docs.kernel.org/admin-guide/kernel-parameters.html).
- Fonte do kernel e scripts locais indicados acima; manifesto JSON anexo contém hashes, cabeçalhos FIT e propriedades DTB examinadas.

