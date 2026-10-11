# Comparação da gravação via U-Boot: ROM Acer T7 v24 e v27

**Atualização após os boots medidos em 10/10:** esta análise trata da tabela e do comando de gravação no U-Boot. Ela não descreve os nomes MTD atribuídos pelo Linux após selecionar `primaryboot`: esses nomes trocaram de lugar entre os dois boots. Ver `CONSOLIDADO_DESCOBERTAS_T7_2026-10-10.md`.

Data: 10/10/2026. Estudo somente de leitura das duas imagens completas locais e de uma consulta ao T7. Nenhuma ROM foi enviada, nenhuma partição foi escrita e nenhum boot foi comandado neste estudo.

## Imagens verificadas

| Versão | Arquivo em `01_FIRMWARES_E_IMAGENS/Stock_OEM_Recovery/` | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| v24 | `nand-4k-ipq5332-single_101000024.img` | 58.259.744 | `b763ed1c5238aeae2e92039cc74d7e87f10e2ea40d4f43ec7c62eded1bb849a1` |
| v27 | `nand-4k-ipq5332-single_101000027.img` | 57.997.600 | `b18c54aabfbad9da22245748e393e63f8b56467e011fac3bdba021f8a91103cc` |

As cópias de mesmo nome em `_FORA DO GitHub/02_FIRMWARES_E_DUMPS_PESADOS/MTD_Full_Dumps/Acer_Predator_Connect_T7/` têm o mesmo SHA-256 das cópias acima. Ambas são FIT/FDT. Seus 22 subcomponentes possuem nós `hash@1` com CRC32; os 22 valores foram recalculados e conferiram em cada imagem.

## A forma de gravação embutida é igual

O componente `/images/script/data` tem **3.503 bytes e SHA-256 `b8e54d3e6c31aa108e140aa18852f6c89e5739784c4f1108b42d02ee125c82ad` nas duas ROMs**. Portanto não há diferença textual no roteiro enviado ao U-Boot:

1. Valida `soc_hw_version` quando informado e valida `machid`.
2. Executa `flashinit nand`, extrai `mibib` e chama `mibib_reload 0 1000 40000 20000000`.
3. Chama `xtract_n_flash` nesta ordem explícita: `0:SBL1`, `0:MIBIB`, `0:BOOTCONFIG`, `0:BOOTCONFIG1`, `0:QSEE`, `0:DEVCFG`, `0:TME`.
4. Chama `xtract_n_flash` para **um** payload `0:CDT` escolhido pelo `machid`.
5. Chama `xtract_n_flash` para `0:APPSBL` e, por último, para o alvo simbólico **`rootfs`** com o payload UBI. Termina com `exit 0`.

Cada operação crítica do script usa `|| exit 1`. O script **não nomeia `rootfs_1`** nem as partições redundantes com sufixo `_1`.

### Conferência do U-Boot OEM no dump local

O dump `_FORA DO GitHub/02_FIRMWARES_E_DUMPS_PESADOS/MTD_Full_Dumps/backup_predator_t7_uboot_appsbl.bin` contém a implementação dos comandos. Na desmontagem ARM/Thumb, `xtract_n_flash` (função em `0x4a40d7c8`) monta `imxtract 0x%x %s && flash %s`: extrai o componente FIT e passa **o mesmo nome de partição** para `flash`. A rotina `flash` (em `0x4a40d2f0`) procura nomes na tabela carregada da MIBIB e tem tratamento específico quando o argumento é a cadeia `rootfs`. Nas rotinas percorridas dessa chamada, não foi encontrada seleção por `primaryboot` nem substituição de `rootfs` por `rootfs_1`.

**Resultado:** as ROMs completas v24 e v27 pedem gravação da partição lógica `rootfs` em toda execução; não há alternância automática A/B nesse roteiro. A MIBIB empacotada atribui endereços distintos a `rootfs` e `rootfs_1`. A gravação também atinge as duas partições `BOOTCONFIG`, além das demais partições comuns listadas acima. O endereço físico usado em cada execução e os bytes efetivamente persistidos continuam dependentes da tabela/estado carregados pelo bootloader e exigem log UART ou leitura posterior para confirmação no aparelho.

A tabela MIBIB comum às duas ROMs traz `rootfs` no bloco `0x59`, endereço `0x01640000`, e `rootfs_1` no bloco `0x419`, endereço `0x10640000`; cada uma reserva `0x3c0` blocos de 256 KiB, ou 240 MiB. A rotina de consulta da tabela no U-Boot (`0x4a400c44`) compara o nome pedido com o nome de cada entrada e devolve seu início/tamanho. Mudar o `primaryboot` seleciona qual sistema iniciar; não rebatiza essas entradas na MIBIB. O registro de inicialização do Slot 2 em `06_DOCUMENTACAO/PROCEDIMENTOS/07_GRAVACAO_SUCESSO_SLOT2_FIRMWARE_V27_2026-10-03.md` também identifica o sistema ativo como `rootfs_1`/MTD20, mantendo `rootfs`/MTD21 como Slot 1.

## O que muda nos dados gravados

Dos 22 payloads, **somente dois diferem** entre v24 e v27:

| Payload FIT | v24 | v27 | Observação |
| --- | ---: | ---: | --- |
| `u-boot-*` para `0:APPSBL` | 565.320 B; SHA-256 `8f89ce21ae4da11a0bc4302b7b563fc65f70ae0269908f11bfe5d1295d413e39` | 565.320 B; SHA-256 `3432d0c417f31cd76835fd3f3a54c6ab0a35476c5ef0fc2ac443073ae9423daf` | 65 bytes diferentes em 19 intervalos: hash de cabeçalho, textos de versão/build e timestamp de gzip. Nenhuma diferença de código encontrada fora desses intervalos. O rodapé de recovery muda `25.01.17` ↔ `25.03.11`. |
| `ubi-*` para `rootfs` | 55.050.240 B = 210 PEBs | 54.788.096 B = 209 PEBs | Um PEB de 262.144 B a menos na v27, no volume `ubi_rootfs`. O conteúdo de sistema/firmware é diferente. |

O `SBL1`, `MIBIB`, `BOOTCONFIG`, `BOOTCONFIG1`, `QSEE`, `DEVCFG`, `TME` e todos os 12 payloads condicionais de `CDT` são byte a byte iguais. As duas `BOOTCONFIG` embutidas em cada FIT também são iguais entre si: 65.536 bytes, SHA-256 `75a6b7ae4845e4523403bac122fbdbd29199815fa38f551c006073e9792771ca`, byte `0x6c = 0`. O `MIBIB` comum tem SHA-256 `e39596e013d7d95ac1636b5e9badf9ced30783b0336fb73162d8719cb229ec9a`. Esses são os valores dos payloads **antes** de qualquer tratamento possível pelo U-Boot; não são leituras pós-gravação da NAND.

Dentro do UBI, as duas imagens têm cabeçalhos EC com `vid_hdr_offset=4096` e `data_offset=8192`. A tabela de volumes apresenta os mesmos nomes e tipos:

| Volume UBI | PEBs presentes v24 | PEBs presentes v27 | PEBs reservados na tabela v24/v27 |
| --- | ---: | ---: | ---: |
| `wifi_fw` | 34 | 34 | 44 / 44 |
| `kernel` | 17 | 17 | 25 / 25 |
| `ubi_rootfs` | 157 | 156 | 157 / 156 |
| `rootfs_data` | 0 | 0 | 1 / 1 |
| Layout UBI | 2 | 2 | interno |

Comparando os dados de cada bloco lógico UBI: em `wifi_fw`, 32 dos 34 PEBs são iguais; em `kernel`, 9 dos 17 são iguais; em `ubi_rootfs`, 2 dos 156 PEBs comuns são iguais. Assim, as duas versões gravam conteúdo diferente também dentro dos volumes de Wi-Fi e kernel, mesmo com a mesma contagem de PEBs nesses dois volumes.

Logo, a diferença de tamanho do FIT completo é explicada exatamente pelo PEB extra no UBI da v24. Ela muda os bytes e o comprimento enviados para `rootfs`, não a sequência de comandos de gravação.

## Relação com o slot observado

Na consulta somente de leitura imediatamente anterior ao estudo, o T7 estava inicializado por `ubi.mtd=rootfs`: `rootfs` correspondia a **MTD 21**, enquanto `rootfs_1` era **MTD 20**. `bootconfig0` e `bootconfig1` tinham `primaryboot=1` e `upgradepartition=rootfs_1`. Esses dados mostram o estado de boot naquela consulta, não a resolução interna do alvo `rootfs` quando o U-Boot processa um FIT de atualização.

Durante esta análise o T7 deixou de responder em `192.168.76.1`; a leitura dinâmica de `xtract_n_flash` não pôde ser concluída. Nenhum comando de escrita ou reinício foi enviado.

## Conclusão e limite da evidência

**Não foi encontrada diferença no método de gravação da v24 para a v27 via o script FIT.** O payload APPSBL muda de identificação/build, mas a comparação direta de seus 565.320 bytes encontrou apenas 65 bytes de metadados diferentes; não há mudança funcional identificada no código de recovery/gravação. O pacote UBI muda em conteúdo e em um PEB do volume `ubi_rootfs`. A desmontagem do U-Boot OEM reforça que esse caminho grava `rootfs` nominalmente a cada envio e não alterna com `rootfs_1`. O estado da NAND, a tabela carregada e o sucesso de cada comando ainda requerem confirmação durante ou após uma gravação real.

O documento `06_DOCUMENTACAO/PROCEDIMENTOS/10_METODO_RECUPERACAO_E_DOWNGRADE_V24.md` atribui um primeiro boot malsucedido à dessincronização de `age`/MIBIB causada pelo downgrade. **Essa causa específica não é demonstrada pelas duas ROMs**: seus payloads MIBIB e BOOTCONFIG são idênticos e o roteiro de gravação também. A observação de recovery após um upload pode ser verdadeira; a atribuição causal requer log UART do U-Boot, resultado de cada `xtract_n_flash` e leitura das partições/BOOTCONFIG após a tentativa. O SHA-256 abreviado da v24 naquele documento também não corresponde ao arquivo v24 verificado aqui.

Referência de sintaxe geral, sem atribuir comportamento OEM ao U-Boot upstream: [FIT e scripts `source`](https://docs.u-boot.org/en/v2024.10/usage/cmd/source.html) e [extração `imxtract`](https://docs.u-boot.org/en/latest/usage/cmd/imxtract.html).
