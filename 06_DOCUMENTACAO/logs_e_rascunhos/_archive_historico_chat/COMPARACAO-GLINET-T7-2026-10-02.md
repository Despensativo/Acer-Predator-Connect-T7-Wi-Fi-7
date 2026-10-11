# Comparacao extraida: GL.iNet IPQ5332 versus Acer Predator T7

Data: 2026-10-02. Escopo: extracao de fontes e auditoria offline. Nenhum acesso, upload, boot, flash ou teste no roteador. Nenhuma alteracao nas fontes originais ou nos candidatos compilados.

## Conclusao

A referencia ajuda principalmente a corrigir e amadurecer o Ethernet do diagnostico sem UART. O codigo efetivamente usado pelo nosso candidato conserva defeitos de propriedade de buffers RX que a referencia corrige. Ha tambem melhorias especificas de filas, tabelas e buffers do IPQ5332.

Nao apareceu nesta extracao um U-Boot substituto nem uma correcao demonstrada para a transicao AArch32 -> AArch64 do Acer. O suporte basico de GCC/NSSCC/PCS/PPE ja existe na nossa arvore; a referencia nao justifica afirmar ausencia total desse suporte.

## Fontes, extracao e verificacao

- Referencia: perceival/openwrt-flint3, commit fixo 2365932733ca8ec3b346621d9cec2eb3df3b2cf3.
- Arvore local: /home/builder/openwrt, HEAD 4daa3c165b5449dec86c2e9b134b62c5c5d6d86a. O HEAD nao descreve sozinho as modificacoes locais: a comparacao usa o conteudo atual dos arquivos.
- Fontes do kernel compilado: /home/builder/t7-chatgpt-work-20261002-v1/linux (scratch reutilizado para v2).
- Extraidos 223 arquivos regulares, 1.695.579 bytes: target/linux/qualcommbe e arquivos generic selecionados por IPQ5332/QPIC/SquashFS/SCM. Nao e copia integral de todos os pacotes OpenWrt nem extracao de firmware comercial binario GL.iNet.
- Todos os arquivos baixados conferidos pelo SHA-1 de objeto Git (cabecalho blob + conteudo) contra a API; SHA-256 e origem registrados.
- Por caminho: 86 arquivos identicos, 14 diferentes, 123 sem arquivo local no mesmo caminho; 21 caminhos locais nao presentes na selecao remota.
- Esses 123 NAO significam 123 correcoes faltantes: varios patches mudaram de numero. O comparador adicional ignora cabecalho editorial e offsets de hunks, preservando o texto do diff. Nao e prova de equivalencia de todo comportamento nem de aplicabilidade automatica.
- DTS Acer-versus-GL e diffs por arquivo preservados em evidencias/diff-glinet-20261002.

## Achados prioritarios

### 1. Defeitos RX presentes no nosso candidato: prioridade alta

Fato observado: em drivers/net/ethernet/qualcomm/ppe/edma_rx.c, linhas 489-510, skb recebe next_skb. O caminho sem netdev libera skb e salta para next_rx_desc antes de atualizar next_skb (atualizacoes nas linhas 519-520 e 531). A iteracao seguinte pode reutilizar o ponteiro liberado.

Na mesma fonte, linha 171 escreve checksum em skb, enquanto a correcao escreve no skb_head vivo. No caminho pskb_may_pull() falhar, linha 350 libera skb e o chamador tambem o libera na linha 525.

A referencia corrige esses tres problemas em 0410-net-ethernet-qualcomm-ppe-fix-freed-skb-reuse-in-rx-reaping.patch. Inferencia: o codigo atual pode causar corrupcao de memoria/panic ao receber pacotes nos caminhos afetados. Precisa confirmar: se algum desses caminhos foi acionado nos boots anteriores. Este achado nao prova a causa do bootloop.

### 2. Melhorias Ethernet ausentes que merecem portabilidade seletiva

A referencia inclui 0371 (store-and-forward do XGMAC), 0372/0374 (fila TX correta e corrida stop/wake), 0375 (tabelas scheduler IPQ5332) e 0376 (budgets BM/QM do IPQ5332).

Fato observado: as fontes locais nao possuem XGMAC_MTL_TXQ_TSF, ipq5332_ppe_sch_bm_config ou ipq5332_ppe_bm_group_config. Sao diferencas reais no kernel preparado, nao apenas nomes de patches. Seus efeitos no T7 exigem validacao; as medicoes descritas nos patches sao de outras placas. O candidato maxcpus=1 reduz a relevancia imediata de problemas ligados a CPUs distintas, mas nao resolve todos os defeitos RX ou TX.

Priorizar correcao de memoria e transmissao basica antes de hardware offload NAT, tuning de desempenho ou Wi-Fi. As series 0411-0456 misturam corretivos comuns e recursos de offload/DSA; nao copiar em bloco.

### 3. Clock: nossa arvore ja tem suporte e uma melhoria adicional

GCC com GPLL0_OUT_AUX, NSSCC, clocks MII em link-up e nos PPE/PCS possuem equivalentes locais. O arquivo compilado gcc-ipq5332.c contem gpll0_out_aux nas linhas 92, 97 e 3078.

Diferenca relevante: a nossa versao de nsscc-ipq5332.c tem tabela dedicada PPE com 300 MHz (linhas 298-310). A referencia consultada ainda associa PPE a tabela CE. Substituir o driver inteiro pela referencia perderia essa melhoria. A referencia tambem adiciona CMN PLL e modelagem XO como fixed-factor: analisar dependencias antes de portar, pois o DTS atual fornece xo_board fixo em 24 MHz.

### 4. FIT: nomes de configuracao dependem do U-Boot de cada placa

Carga base 0x41000000 e comum a receita GL e ao nosso candidato. O BE9300 usa config-1 e gzip; BE6500 usa config@mi01.2; Acer usa config@mi01.6 e LZMA. Mesmo SoC nao implica mesmos nomes ou formato.

O bootscript factory do BE9300 executa flashinit/flupdate e flash 0:HLOS/rootfs. Ele grava armazenamento e nao serve como acionador para boot temporario pela RAM. Foi somente lido.

O codigo GL nao valida nossas areas temporarias para FIT, pilha/heap do bootloader ou fixups de RAM. Os requisitos pendentes do acionador continuam.

### 5. NAND/UBI: referencia util, geometria diferente

BE6500 habilita qpic_nand, SPI NAND, ECC 8/512 e particoes via SMEM. Nossa fonte ipq5332.dtsi compilada ainda nao tem esse controlador. O DTS Acer original tambem nao o habilita.

Isso e uma lacuna para instalar um sistema persistente. Para o candidato initramfs de diagnostico, MTD desativado e deliberado: nao precisa montar a NAND.

A receita BE6500 tem NAND 2 KiB / bloco 128 KiB e particoes/tamanhos proprios. Nao usar esses valores na NAND 4K do T7 nem copiar root=/dev/ubiblock0_1, pois o indice depende da ordem de attach. Preservar associacao real MTD/slot e volumes Acer.

### 6. Logs persistentes sem UART: pista concreta, endereco nao validado no Acer

O DTS BE9300 define ramoops 1 MiB em 0x4da00000. Comentarios relatam verificacao contra mapa de memoria em execucao no Flint. Isso e evidencia do autor sobre sua placa, nao teste nosso.

No candidato Acer, 0x4d300000-0x4db00000 permanece reservado como conservative-gap, incluindo 0x4da00000. Nao retirar essa reserva com base na outra placa. Mesmo um endereco livre exige demonstrar retencao apos o tipo de reset e um boot de resgate capaz de ler o buffer. Nosso kernel tem PSTORE/RAM, mas sem regiao ramoops habilitada.

### 7. SCM/TrustZone: distinguir CPU principal de coprocessador

O patch remoto 2008 modifica qcom_scm_pas_init_image() para metadados de firmware de periferico/coprocessador, com consulta de disponibilidade e fallback. Nao e a chamada do U-Boot que troca a CPU para ARM64. Esta extracao nao demonstra a compatibilidade da TrustZone Acer com o boot desejado.

As series Q6/WCSS/ath12k podem ajudar Wi-Fi em etapa posterior, dependem de firmware/calibracao especificos e nao sao necessarias para o primeiro initramfs sem Wi-Fi.

## Rota recomendada

1. Criar futuramente uma copia v3 isolada a partir do candidato atual, preservando v1/v2.
2. Portar seletivamente correcao RX 0410 e corretivos basicos TX, revisando dependencias e os valores especificos do SoC.
3. Conferir DTS e modo dos links contra evidencias Acer: o GL usa switch Realtek/10gbase-r e WAN usxgmii; o nosso DTS usa QCA8084 e 2500basex. Sem prova da ligacao eletrica real, nao copiar a topologia GL.
4. Recompilar e verificar offline mantendo initramfs, sem MTD, modulos ou mecanismo de instalacao. Ainda nao foi feito nesta comparacao.
5. So depois de resolver o acionador e confirmar Slot 1 recuperavel, avisar o usuario antes de qualquer teste pela RAM.

Ausencia de pacote UDP continua inconclusiva quanto ao ponto de falha; sucesso precisa de identidade do novo kernel, arquitetura, release e boot_id, conforme coletor v2.

## Integridade preservada

.config original: SHA-256 2e14935e4f2a3cc872b5934f2b4ad0abd525a93fbd13b1322d148de12f2d88c8.
FIT v2: SHA-256 76d8a9969cd44b723ac9e4e092a9f27aad08a84f61be126d7af7d7b537ed3373.
Conferidos ao final e iguais aos valores anteriores.

Fontes externas: https://github.com/perceival/openwrt-flint3/tree/2365932733ca8ec3b346621d9cec2eb3df3b2cf3/target/linux/qualcommbe . As evidencias locais detalham URLs individuais, linhas e hashes. Scripts baixados nao executados.