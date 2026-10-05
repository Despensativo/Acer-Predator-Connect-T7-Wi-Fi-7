# Protótipo OpenWrt 6.18 para Acer Predator Connect T7

Data: 2026-10-03. Trabalho offline em disco interno; nenhum comando foi enviado ao roteador.

## Fontes e origem

- Árvore pública `perceival/openwrt-flint3`, branch `flint3-be9300`, commit `2365932733ca8ec3b346621d9cec2eb3df3b2cf3`.
- Feed público `packages`, commit `0774799a271fc22724fae6f7ee32f5df932cc08a`.
- DTS candidato local `03_ENGENHARIA_REVERSA/DeviceTree_DTS/ipq5332-acer-predator-t7.dts`, tratado como ponto de partida, não como descrição validada de todo o hardware.
- Mapa de RAM e reservas fixas selecionados do DTB capturado do T7 (`acer_predator_t7.dts` no projeto): 1 GiB a partir de `0x40000000`. O arquivo genérico `fdt_mi01_6.dts` aponta 512 MiB, portanto não foi usado para o tamanho de RAM. Reservas de bootloader, SBL, TZ, SMEM e WCSS já constam de `ipq5332.dtsi` no kernel 6.18.39; o DTS T7 somente adiciona as regiões ausentes e redefine o tamanho do nó de memória existente.

## Escopo do primeiro build

O perfil novo `acer_predator-t7` define apenas um FIT initramfs. `IMAGES :=` remove receitas persistentes do perfil; não há imagem factory ou sysupgrade do T7 nesta etapa. O PCIe do rádio do DTS candidato foi desabilitado; firmware Wi-Fi específico e calibração da unidade não foram incluídos. MACs zerados de preenchimento foram removidos.

## Bloqueios conhecidos

- A árvore Flint 3 não contém um driver QCA8386 para o switch do T7. LAN, WAN, VLAN e aceleração não estão validadas.
- O DTS candidato anterior foi escrito para um build antigo e não é um porte completo do DTB OEM. Pinos, PHYs, relógios, reservas, rádio e nomenclatura de interfaces exigem conferência por hardware.
- A existência do FIT e a validação de seus hashes não demonstram que o U-Boot Acer carregue o kernel AArch64, nem que haja saída de rede ou console. Um envio HTTP anterior foi reconhecido sem prova de execução do kernel.
- O fato de o APPSBL Acer ser AArch32 não impede, por si, boot de kernel AArch64. O backup `appsbl.bin` do T7 contém a mensagem `Jumping to AARCH64 kernel via monitor` no offset 448861. Em fonte QSDK comparável, `bootm` reconhece o cabeçalho ARM64 e chama `jump_kernel64`, que solicita a transição ao monitor seguro. Isso é evidência forte de suporte no U-Boot Acer, mas não prova que nosso FIT chegue a esse ponto ou que a TrustZone aceite esta imagem. Não há justificativa para atualizar o U-Boot apenas pela diferença 32/64 bits.
- Nenhuma hipótese TFTP deve ser convertida em procedimento sem leitura de ambiente e captura passiva de tráfego do T7 real.

## Resultado

`make -j12` terminou com código 0 em 2026-10-03, após corrigir o ambiente WSL para usuário não privilegiado e PATH Linux limpo. O log final está em `/home/builder/t7-full-final.log`; os problemas intermediários e respectivas correções estão registrados em `TASK.md`.

- Artefato: `openwrt-qualcommbe-ipq53xx-acer_predator-t7-initramfs.itb` (8.305.020 bytes).
- SHA-256 final: `04fb7b7075a3bbec524dddc969aa8ac941aade27ffb4142c39e7586fc341fc8d`.
- Kernel: Linux 6.18.39, ARM64; FIT com kernel LZMA, FDT T7 e configuração padrão `config@mi01.6`.
- `validate_candidate.py` extraiu os dois componentes do FIT e conferiu os quatro hashes internos (CRC32 e SHA1), tamanhos, compatibilidade, mapa de RAM e reservas de memória. Resultado: `validation.json`, `structural_pass: true`.
- A imagem final foi recriada na etapa completa do build; o hash acima substitui o hash provisório obtido após `target/linux/install`.
- `t7-source.patch`, `openwrt.config`, `config.seed`, `t7.manifest` e scripts locais registram as alterações e a configuração. Não houve boot em hardware, validação de switch, Wi-Fi ou instalação.

`dumpimage` emitiu o aviso `Image contains unit addresses @, this will break signing`. O FIT não foi assinado nem testado com secure boot. A data de criação interna do FIT reflete o carimbo reprodutível da fonte, não a data desta compilação.

Análise posterior do APPSBL Acer confirmou a comparação do magic ARM64 e o salto pelo monitor seguro no código do próprio T7. O mapa estático do FIT cabe nos intervalos candidatos, mas o caminho HTTP/TFTP e a memória dinâmica do bootloader ainda requerem teste. Ver `BOOT_PATH_STATIC.md`. O diagnóstico mínimo v3 anterior (Linux 6.18.52, sem MTD/shell) é preferível ao primeiro teste de passagem ARM64; este OpenWrt completo 6.18.39 fica para a etapa seguinte.
