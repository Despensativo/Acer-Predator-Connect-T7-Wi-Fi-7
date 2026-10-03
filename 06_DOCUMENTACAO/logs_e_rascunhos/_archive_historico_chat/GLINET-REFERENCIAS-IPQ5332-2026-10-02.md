# Referencias GL.iNet para o Predator T7

Data: 2026-10-02. Pesquisa web e leitura de codigo; nenhum acesso ou teste no roteador.

## Fato observado

O port comunitario do Flint 3 GL-BE9300 declara IPQ5332 e kernel 6.18. O autor relata boot, SSH e Ethernet funcionando, com falhas de estabilidade ainda abertas. Isso e relato do autor, nao validacao nossa nem suporte oficial incorporado ao OpenWrt.

A mesma arvore inclui GL-BE6500 (Flint 3e), mas o mantenedor nao o testou. No DTS consultado, ele habilita QPIC SPI NAND, ECC 8/512 e particoes SMEM. A receita usa paginas NAND de 2048 bytes e bloco de 128 KiB: nao copiar para o T7 com NAND 4K.

O BE9300 usa eMMC e Ethernet Realtek. Ambos sao referencias do mesmo SoC, mas nao imagens intercambiaveis com o Acer.

A tabela oficial GL.iNet classifica o firmware comercial dos dois como QSDK/OpenWrt 23.05. Esse firmware difere do port comunitario com kernel 6.18.

## Inferencia e utilidade

Comparar patches comuns de IPQ5332, clocks, SCM, PPE/EDMA, FIT e inicializacao ARM64 pode reduzir as variaveis do nosso diagnostico. Para armazenamento, BE6500 e a referencia mais proxima; para resultados publicados, BE9300 tem evidencia mais forte.

O DTS BE9300 inclui ramoops em 0x4da00000 e comenta reservas observadas em execucao. Isso inspira investigacao de logs persistentes sem UART, mas NAO valida esse endereco, retencao de RAM ou mapa QSEE no T7. Copiar a reserva seria inadequado.

## Precisa confirmar / proximo passo

Fazer diff offline entre os patches compartilhados e nossa arvore, depois separar alteracoes especificas de placa. Priorizar Ethernet para os logs UDP ja preparados, configuracao ARM64 e contrato FIT. Manter DTS, calibracao, particoes e bootloader do Acer. Nao instalar firmware, U-Boot, QSEE ou CDT GL.iNet no T7. Nao iniciar teste sem avisar o usuario.

## Fontes e reproducibilidade

- Port e relatos do autor: https://github.com/perceival/openwrt-flint3
- Firmware oficial: https://www.gl-inet.com/en-gb/pages/firmware-versions
- Produto BE6500: https://www.gl-inet.com/products/gl-be6500/
- Snapshot consultado: 2365932733ca8ec3b346621d9cec2eb3df3b2cf3.
- Copias de referencia (DTS dos dois modelos e receita ipq53xx.mk), URLs e SHA-256: fontes/referencia-glinet-20261002/proveniencia.json.

Conclusao: referencia concreta e promissora para desenvolvimento; ainda nao demonstra compatibilidade do boot ARM64 com o firmware seguro do Acer.