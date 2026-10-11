# ImmortalWrt: utilidade para o Acer Predator T7

Pesquisa em 2026-10-02, somente leitura do projeto original e preparacao documental local. Nenhum acesso ou teste no roteador. Nenhum patch aplicado.

## Conclusao

Ha um corretivo aproveitavel de Ethernet PPE/EDMA, mas nao foi encontrada uma definicao pronta do T7, GL-BE6500 ou GL-BE9300 nem o subtarget ipq53xx nas branches oficiais master, openwrt-24.10 e openwrt-25.12 examinadas. Isso nao exclui branches de terceiros, PRs ou trabalho nao publicado.

Na master, qualcommbe seleciona somente ipq95xx. O fato de alguns patches mentionarem IPQ5332 em qualcommax nao representa suporte completo a uma placa IPQ5332.

## Achado util: direcao DMA e limpeza dos buffers RX

Patch: target/linux/qualcommbe/patches-6.18/0362-net-ethernet-qualcomm-ppe-fix-rx-dma-mapping-direction.patch.

Fato observado no nosso scratch usado pelo candidato v2:

- edma_rx.c:61 e :80 mapeiam buffers RX com DMA_TO_DEVICE.
- edma_rx.c:495 e :497 liberam os mesmos tipos de mapeamento com DMA_FROM_DEVICE.

O patch corrige a direcao de mapeamento para DMA_FROM_DEVICE, acrescenta unmap na limpeza de rings e leitura dos registradores apos desativacao para garantir conclusao das escritas antes da limpeza.

A referencia GL anteriormente extraida ja corrige a direcao em 0420 e trata limpeza em 0421. Assim, nao aplicar duas series sobrepostas sem comparar os hunks. O ImmortalWrt e uma segunda fonte de revisao, com leitura de registradores explicitamente incluida.

Inferencia: a incongruencia local precisa ser corrigida pela API DMA; ainda nao prova uma falha de cache ou a causa do bootloop neste SoC. A referencia GL inclusive ressalva que nao conhece mau funcionamento demonstrado da direcao nessa plataforma.

## TrustZone: outra etapa do sistema

Na master foram encontrados 0185 (tamanho de metadata PAS) e 0803 (MSA lock/unlock), sob qualcommax/patches-6.18. Os dois tratam firmware de perifericos/coprocessadores e remoteproc. Podem ajudar o Wi-Fi posteriormente; nao sao uma solucao para o U-Boot colocar a CPU principal em AArch64. O primeiro consulta disponibilidade e mantem fallback para a chamada anterior.

## Recomendacao

Manter a referencia GL/IPQ5332 como base principal para comparar o SoC. Incluir o corretivo DMA ImmortalWrt na revisao do futuro candidato v3, junto da correcao de propriedade skb RX ja identificada. Preservar a topologia, calibração, memoria e NAND do Acer. Nao migrar a compilacao inteira para outro target nem usar imagem de uma placa ipq95xx/ipq50xx/ipq60xx/ipq807x no T7.

## Evidencias preservadas

Inventarios completos de caminhos filtrados e arquivos consultados: fontes/referencia-immortalwrt-20261002. As respostas Git tree de todas as branches consultadas vieram truncated=false.

Commits consultados:

- master: 5233c153ef7f119c567b54a92feea6919b167e84
- openwrt-24.10: 5f7bc1b1aab99c61e7555f70201e75b9e0c97aa3
- openwrt-25.12: 313718c25f206cdeee399bdc6c002b7388c9a513

Fontes primarias:

- https://github.com/immortalwrt/immortalwrt/tree/5233c153ef7f119c567b54a92feea6919b167e84/target/linux/qualcommbe
- https://github.com/immortalwrt/immortalwrt/blob/5233c153ef7f119c567b54a92feea6919b167e84/target/linux/qualcommbe/patches-6.18/0362-net-ethernet-qualcomm-ppe-fix-rx-dma-mapping-direction.patch

O escopo nao inclui auditoria de todos os forks que utilizam o nome ImmortalWrt. Os encontrados na busca com NSS sao projetos de terceiros, nao prova de suporte oficial ao T7.