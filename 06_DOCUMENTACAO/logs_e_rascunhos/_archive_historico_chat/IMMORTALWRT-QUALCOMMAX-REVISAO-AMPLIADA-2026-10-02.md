# ImmortalWrt qualcommax/patches-6.18 — revisão ampliada para o T7

Commit fixo: 5233c153ef7f119c567b54a92feea6919b167e84. Revisão offline em 2026-10-02. Nenhum patch aplicado e nenhum acesso ao roteador.

## Conclusão

Sim, esta pasta contém mais referências úteis do que os dois patches SCM destacados no levantamento anterior. Foram extraídos os 93 patches, total 728.419 bytes, com verificação individual de Git blob SHA-1 e registro SHA-256. O inventário Git veio truncated=false. Há 18 patches com menções a IPQ5332, mas algumas são contexto ou texto de bindings, não nova implementação para o SoC.

A principal novidade útil é a série WCSS seguro + Q6 multipd, que inclui compatíveis explícitos para IPQ5332. Há também correções/referências de NAND/QPIC e refatoração do PHY compartilhado PCIe/USB3. Não há perfil completo do Acer, correção direta de SquashFS, ramoops/netconsole ou gcc-ipq5332 nesta pasta.

## 1. Wi-Fi: firmware seguro do Q6/WCSS

0186 documenta os bindings. 0188 adiciona drivers/remoteproc/qcom_q6v5_wcss_sec.c, CONFIG_QCOM_Q6V5_WCSS_SEC e compatible qcom,ipq5332-wcss-sec-pil. O recurso IPQ5332 usa PAS ID 0xd e ss_name q6wcss. Carrega firmware MDT e pede autenticação/inicialização via qcom_scm_pas_auth_and_reset. Não contorna a TrustZone: usa seus serviços.

Fonte:
https://github.com/immortalwrt/immortalwrt/blob/5233c153ef7f119c567b54a92feea6919b167e84/target/linux/qualcommax/patches-6.18/0188-remoteproc-qcom-add-hexagon-based-wcss-secure-pil-driver.patch

0801 e 0804–0815 tratam o modelo de múltiplos domínios de proteção, inicialização do Q6, rádios dependentes, firmware segmentado, SCM/MDT, clocks e bootargs do coprocessador. 0805 adiciona qcom_q6v5_mpd.c com suporte IPQ5332; deve ser analisado como série com dependências. Esses bootargs são do Q6/firmware, não a cmdline do Linux principal.

No scratch do candidato v2 não existem qcom_q6v5_wcss_sec.c nem qcom_q6v5_mpd.c. Há o WCSS anterior e CONFIG_QCOM_Q6V5_WCSS=y, mas isso não equivale ao suporte seguro/multipd desta série. A ausência de um arquivo específico não é prova de ausência de todas as funcionalidades equivalentes possíveis.

Aplicação: referência importante para a fase Wi-Fi do port mainline. Exige firmware compatível, calibração do Acer, reservas de memória, interrupções, clocks, SMEM e DTS corretos. Não entrega por si só Wi-Fi 7 completo nem prova que o firmware Acer aceita os mesmos parâmetros.

0184 é mailbox TME-L com compatible ipq5424-tmel. Em 0188, o IPQ5424 habilita use_tmelcom; o IPQ5332 não. Não atribuir esse transporte TME-L ao T7 sem evidência.

## 2. NAND/QPIC: útil para boot pela flash, com condições

0401 trata chips que anunciam requisito mínimo ECC de 1/2 bits, aceitando 4 bits no QPIC-SNAND quando o requisito vem do chip. A versão local não contém esse tratamento. Não é um pedido para reduzir o ECC Acer: a leitura de páginas existentes precisa respeitar o layout real usado na flash. Exigências de step 512 e ECC 8 observadas nas referências de placa devem ser validadas para o Acer.

0411 limita a comparação de ID NAND paralelo aos quatro bytes disponíveis no registrador QPIC. 0412 limita a comparação SPI-NAND a três bytes após o fabricante. Na fonte local ainda há comparação do comprimento completo. São candidatos para investigar falhas reais de identificação, especialmente na via SPI-NAND pertinente ao DTS proposto.

Importante: esses patches alteram os caminhos genéricos nand_base.c e spi/core.c sem restringir o comportamento ao controlador QPIC. Podem introduzir identificação ambígua para outros chips. Não aplicar cegamente; confirmar ID e revisar uma solução delimitada ao hardware.

Fonte:
https://github.com/immortalwrt/immortalwrt/blob/5233c153ef7f119c567b54a92feea6919b167e84/target/linux/qualcommax/patches-6.18/0412-mtd-spinand-qpic-only-support-max-4-bytes-ID.patch

0400 adiciona a NAND Toshiba TH58NYG3S0HBAI4, página 4 KiB, OOB 256 e ECC 8/512, originalmente testada no Arcadyan AW1000. Não foi confirmado esse modelo no Acer; a semelhança de geometria não basta para adotá-la. A patch depende da identificação tratada em 0411.

O candidato diagnóstico local tem CONFIG_MTD desabilitado e boot por initramfs. Esses ajustes não desbloqueiam seu boot inicial em RAM; ganham relevância na fase NAND/UBI de uma imagem persistente.

## 3. PHY PCIe/USB3

0150–0155 documentam/refatoram o UNIPHY compartilhado por IPQ5332 e IPQ5018. 0154 restaura o reset se o enable de clocks falhar. Essa é uma correção útil de tratamento de erro, sujeita a portabilidade para a implementação local. 0155 adiciona os detalhes USB3 para IPQ5018: não extrapolar a sequência para IPQ5332 automaticamente.

Na fonte local permanece phy-qcom-uniphy-pcie-28lp.c, com compatible IPQ5332, e não existe o arquivo renomeado pcie-usb3-28lp. Portanto não é ausência de suporte PCIe básico, mas diferença de revisão/implementação. Não deve ser prioridade para o diagnóstico Ethernet em RAM que mantém PCIe desligado.

## 4. TrustZone/PSCI: referência diagnóstica, não solução ARM64

0903 desabilita OSI no IPQ6018 porque algumas versões QSEE anunciam suporte, mas travam ao usá-lo até o watchdog reiniciar o aparelho. É um exemplo documentado de falha entre Linux e firmware seguro com sintoma de reset. Atua na função psci_has_osi_support dentro do Linux já iniciado.

O filtro da patch é of_machine_is_compatible("qcom,ipq6018"). Não cobre o IPQ5332. Na fonte local esse filtro não existe, mas isso não prova que o T7 tenha o mesmo defeito. Não modificar o filtro para IPQ5332 sem evidência de versão/capacidades/fluxo PSCI. Não é a SMC que passa a CPU principal de AArch32 a AArch64.

Fonte:
https://github.com/immortalwrt/immortalwrt/blob/5233c153ef7f119c567b54a92feea6919b167e84/target/linux/qualcommax/patches-6.18/0903-psci-dont-advertise-OSI-support-for-IPQ6018.patch

0185 (metadata PAS) e 0803 (MSA lock/unlock) já haviam sido documentados. Continuam úteis na série de firmware de coprocessadores, não como bypass da passagem ARM64.

## 5. Não copiar o hack de bootargs sem corrigir

0911 implementa bootargs-find/replace no /chosen e poderia substituir ubi.mtd sem alterar o ambiente persistente. Contudo, declara r_len sem inicializar e o usa em strncmp(cmdline,p,r_len) no ramo exact-match antes de obter r_len na leitura da propriedade de substituição. É um defeito concreto nessa versão da patch, especialmente no primeiro ciclo de exact-match. Não é uma garantia de substituição segura.

A fonte local não tem esse hack; o candidato usa CONFIG_CMDLINE_FORCE=y. Para a fase de diagnóstico não é necessário introduzi-lo. Mesmo corrigido, ele executa dentro do Linux: não troca a partição da qual o U-Boot carrega o kernel, não impede gravação no volume errado e não valida bootm/FIT.

Fonte:
https://github.com/immortalwrt/immortalwrt/blob/5233c153ef7f119c567b54a92feea6919b167e84/target/linux/qualcommax/patches-6.18/0911-arm64-cmdline-replacement.patch

## 6. Ethernet e diferenças de família

0951–0953 adicionam opções Kconfig/Makefile para PCS_QCA_UNIPHY, QCOM_80211AX_PPE e QCOM_EDMA. Não contêm nesse trecho toda a implementação dos drivers e não são substituição direta do PPE/PCS IPQ9574 usado na família 802.11be do candidato T7. 0954 é DWMAC IPQ5018. Não trocar drivers apenas pela palavra PPE.

O corretivo RX DMA relevante destacado antes continua em qualcommbe/patches-6.18/0362, fora da pasta qualcommax perguntada. Deve ser revisado junto dos corretivos GL para não duplicar mudanças.

## Comparação e limites

Foi comparado o payload normalizado dos 93 patches com a série qualcommbe local e a referência GL salva: um match exato em cada. Essa normalização ignora cabeçalhos e offsets de hunks, mas ainda é estrita; não encontrar match NÃO demonstra ausência de funcionalidade nem falta de 92 patches. As verificações nos arquivos efetivos citadas acima são a evidência mais específica.

Não foram aplicadas patches, feitos dry-runs de aplicação, compilados novos kernels ou testado hardware nesta revisão. A extração não executou scripts do repositório remoto.

Integridade local conferida: .config original SHA-256 2e14935e4f2a3cc872b5934f2b4ad0abd525a93fbd13b1322d148de12f2d88c8; FIT candidato v2 SHA-256 76d8a9969cd44b723ac9e4e092a9f27aad08a84f61be126d7af7d7b537ed3373, iguais aos registros anteriores.

## Ordem recomendada

1. Diagnóstico em RAM: consolidar corretivos Ethernet já identificados e observar execução antes de acrescentar subsistemas.
2. Boot persistente: identificar NAND, ajustar DTS/MTD/QPIC/UBI e avaliar 0401/0412 apenas conforme necessidade real.
3. Wi-Fi: portar a série segura/multipd necessária e validar firmware/DTS/calibração específicos do Acer.
4. PCIe/USB e PSCI: revisar conforme sintomas/capacidades reais, preservando a separação entre SoCs.

## Evidências preservadas

fontes/immortalwrt-qualcommax-auditoria-5233c153/: inventario.json, proveniencia.json, comparacao-local-gl.json e patches/ com os 93 arquivos. Origem de cada patch e seus hashes estão registrados. Scripts próprios: ferramentas/extrair_qualcommax_immortalwrt.py e comparar_qualcommax_immortalwrt.py.

Este relatório amplia o levantamento anterior, que priorizou busca por nomes IPQ5332 e corretivos DMA. Não demonstra suporte completo ao Acer nem resolve sozinho o boot ARM64.
