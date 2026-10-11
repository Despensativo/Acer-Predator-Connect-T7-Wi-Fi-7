# ROM stock no Slot 2: Linux funcional e Web Recovery

**Atualização posterior no mesmo dia:** o estado `primaryboot=0` já iniciou a stock v27 com BOOTCONFIG integral e sem `fsbootargs`; um ensaio de dois marcadores mostrou overlays separados. Os FITs V2 foram gerados offline, mas o teste de Web Recovery foi adiado. Ver `CONSOLIDADO_DESCOBERTAS_T7_2026-10-10.md` antes de usar os planos históricos abaixo.

Data: 10/10/2026. Análise somente de leitura. Nenhuma partição do T7 foi escrita e nenhum FIT foi enviado neste estudo.

## Estado confirmado no aparelho nesta análise

Em `192.168.76.1`, `/proc/cmdline` indica `ubi.mtd=rootfs`; `/sys/class/ubi/ubi0/mtd_num` indica `21`. `/proc/mtd` lista `mtd21` como `rootfs` e `mtd20` como `rootfs_1`, ambos com `0x0f000000` bytes (240 MiB). O primeiro cabeçalho de cada uma começa com `UBI#`; isso não comprova a integridade completa do Slot 2. Somente o `ubi0` do Slot 1 estava anexado. Seus volumes 0–3 se chamam `wifi_fw`, `kernel`, `ubi_rootfs` e `rootfs_data`.

Os dois objetos `/proc/boot_info/bootconfig{0,1}` tinham `age=3`; `rootfs/primaryboot=1` e `rootfs/upgradepartition=rootfs_1`. `fw_printenv fsbootargs` informou variável ausente; `bootcmd=bootipq`. Há seletores separados no BOOTCONFIG para `0:APPSBL`, `0:CDT`, `0:DEVCFG`, `0:HLOS`, `0:WIFIFW` e `rootfs`; não existe um único interruptor físico que selecione todas as cópias `_1` em bloco.

As entradas `_1` têm áreas NAND distintas. Leitura e SHA-256 dos pares de MTD mostraram, por exemplo, `QSEE`/`QSEE_1` iguais, mas `SBL1`/`SBL1_1`, `DEVCFG`/`DEVCFG_1`, `TME`/`TME_1`, `CDT`/`CDT_1` e `APPSBL`/`APPSBL_1` diferentes. Isso demonstra que não são links nem espelhamento automático. Os números `mtd25`–`mtd28` apresentados enquanto `ubi0` está anexado são dispositivos dos volumes UBI, não mais quatro partições físicas MIBIB.

O SHA-256 lido ao vivo de `/dev/mtd15` (`APPSBL`) foi `3d6281190512ba50b83eea1a2d6fca69f01da5bb390d52b601e762ce8f1df2fc`, igual ao dump local desmontado abaixo. O SHA-256 de `/dev/mtd2` (`MIBIB`) foi `880049c43e55aeef60b9d683fe367092f27e61510092a97f92a2fdcf31db30a2`, igual ao dump local do mapa. Assim, a análise estática se aplica aos bytes atuais dessas duas partições do aparelho, embora não substitua um teste de gravação.

## Fonte stock e objetivo recomendado

O FIT oficial v27 `nand-4k-ipq5332-single_101000027.img` traz uma imagem UBI de 54.788.096 bytes, com `wifi_fw`, `kernel`, `ubi_rootfs` e a tabela de `rootfs_data`. O script OEM aponta sua gravação para `rootfs`, além de outras nove áreas, e não nomeia `rootfs_1`. A análise estática do FIT v24 mostra o mesmo roteiro de gravação.

O primeiro objetivo útil é instalar **o sistema stock completo no `rootfs_1`** mantendo `SBL1`, `QSEE`, `DEVCFG`, `TME`, `CDT`, `APPSBL`, `MIBIB`, `ART` e o Slot 1 como estão. Regravar todas as seis cópias pequenas `_1` é outra operação: aumenta o risco e não é requisito demonstrado para iniciar o Linux do `rootfs_1` neste aparelho. `BOOTCONFIG`/`BOOTCONFIG1` e o ambiente `APPSBLENV` são controles compartilhados, não conteúdo exclusivo do Slot 2.

## Cenário A — Linux inicia normalmente

1. Confirmar novamente por nome de partição e `ubi.mtd=` qual slot está em uso. Não confiar somente no número `mtd20`, que é uma observação deste boot.
2. Validar SHA-256 do FIT oficial e de seus componentes, conferir que o alvo `rootfs_1` não está montado e fazer backup do conteúdo/dados do Slot 2 que se deseje guardar.
3. Anexar a partição **inativa** ao UBI e conferir `mtd_num`, nomes, tipos e tamanhos dos quatro volumes antes de qualquer escrita. Se a tabela UBI existente não for válida, o procedimento por volume não serve; será necessário um caminho de reconstrução do contêiner.
4. Para preservar a tabela UBI existente, atualizar `wifi_fw`, `kernel` e `ubi_rootfs` com os três componentes da **mesma versão stock** usando `ubiupdatevol`. Tratar `rootfs_data` separadamente: mantê-lo preserva configurações antigas; truncá-lo após backup produz uma instalação limpa, mas apaga os dados do Slot 2. Uma imagem UBI integral exigiria `ubiformat -f`, que apaga/recria todo o contêiner e precisa de validação específica de geometria e bad blocks antes do uso.
5. Verificar retornos e hashes/leitura dos volumes, desmontar/desanexar o UBI inativo e só depois selecionar o Slot 2. Confirmar após o boot `ubi.mtd=rootfs_1`, vínculo UBI com a partição esperada, kernel, Wi-Fi, rootfs, overlay e rede. Se falhar, usar o alternador testado para voltar ao Slot 1.

Este caminho já tem precedente local de gravação do v27 por volumes e boot em `rootfs_1` (`06_DOCUMENTACAO/PROCEDIMENTOS/07_GRAVACAO_SUCESSO_SLOT2_FIRMWARE_V27_2026-10-03.md`). O precedente não valida automaticamente um novo pacote ou o estado atual do Slot 2.

## Cenário B — Linux não inicia, mas o Web Recovery do U-Boot responde

O recovery só pode agir sobre o que seu U-Boot ainda consegue acessar: rede, RAM, NAND e mapa MIBIB. Um FIT de resgate destinado ao Slot 2 deve ser **separado** da ROM stock original e conter ao menos o payload UBI stock e um script que inicialize NAND, extraia esse payload para RAM e mande gravá-lo em `rootfs_1`, interrompendo ao primeiro erro. O script OEM não serve sem modificação, pois nomeia `rootfs` e regrava componentes compartilhados/primários.

No dump APPSBL deste T7, a rotina `flash` para NAND consulta o nome solicitado na tabela MIBIB (`0x4a400c44`, chamada em `0x4a40d37a`). Quando encontra a entrada, recebe início e tamanho, verifica que a imagem cabe na partição (`0x4a40d414`–`0x4a40d422`) e monta comandos `nand erase` para a **área reservada inteira** seguidos de `nand write` para o **comprimento da imagem** (`0x4a40d6b4`–`0x4a40d700`). Como a MIBIB contém `rootfs_1` a partir de `0x10640000` por 240 MiB, o caminho nominal não depende de renomear `rootfs` dinamicamente: `flash rootfs_1` tem um destino físico distinto na análise estática. Isso é mais forte que uma simples suposição de sintaxe, mas **não é um teste de gravação**. Ainda faltam aceitação do FIT pelo Web Recovery, resultado real de `flash rootfs_1`, tratamento de bad blocks, verificação de leitura posterior e boot do sistema. A mensagem genérica de arquivo pequeno/grande da página não estabelece uma regra de tamanho específica.

Procedimento de resgate em duas etapas, a validar em bancada:

1. Enviar o FIT que grava **somente** `rootfs_1`, mantendo a seleção atual. Obter a saída/resultado do Web Recovery e, se possível, uma verificação de leitura. Não marcar sucesso apenas porque o upload HTTP terminou.
2. Reentrar no recovery e enviar o seletor do Slot 2, que sincroniza os dois BOOTCONFIG com `fsbootargs` em `APPSBLENV`. O seletor do Slot 1 teve êxito relatado pelo usuário; o desta geração para Slot 2 ainda não foi validado. Se não houver Linux para verificar entre as etapas, o primeiro estágio ainda pode ser repetido sem atingir o Slot 1.

Um FIT único que grave `rootfs_1` e depois selecione o Slot 2 pode ser estudado depois. Ele reduz a operação manual, mas combina mais gravações persistentes não atômicas e não elimina a necessidade de testar leitura e boot. Na análise inicial, nenhum pacote de resgate havia sido construído ou enviado.

### Reavaliação após os testes de 10/10/2026

Uma `.bin` de Web Recovery pode ser um FIT com o payload UBI integral OEM v27 e um script que grave `rootfs_1`, verifique a escrita e então selecione o Slot 2 em BOOTCONFIG/BOOTCONFIG1 e no ambiente necessário a `bootipq`. A extensão `.bin` não altera o formato FIT. A rotina `flash rootfs_1` e a aceitação desse FIT completo pelo Web Recovery ainda não foram ensaiadas. O pacote não deve regravar MIBIB, ART nem as cópias pequenas `_1` já verificadas como v27.

O benefício esperado precisa ser delimitado: em 10/10, o Slot 2 já recebeu a imagem UBI integral stock v27 via `ubiformat`; seus volumes de sistema foram lidos de volta com hashes idênticos aos OEM e falhou em três boots. Um FIT de um arquivo testaria principalmente **outro caminho de gravação e seleção de boot**, sem mudar kernel, Wi-Fi ou SquashFS. Por isso, antes de um pacote que grava e seleciona em um só envio, o ensaio mais informativo é separar a gravação com leitura de volta da comutação. Se o problema estiver em argumentos/seleção de `bootipq`, uma nova gravação do mesmo UBI não o resolverá. A primeira exceção do Linux ainda precisa ser capturada.

Foram gerados offline dois FITs candidatos com extensão `.bin` em `04_SCRIPTS_E_FERRAMENTAS/Recovery_Stock_V27_Slot2/`: o primeiro contém o UBI OEM v27 e nomeia somente `rootfs_1`; o segundo é cópia byte a byte do seletor de Slot 2 existente. O `README.md` dessa pasta registra composição, hashes e verificações. Nenhum dos candidatos foi enviado ao T7; os alternadores originais continuam intactos. A validação ao vivo de aceitação, gravação e boot segue pendente.

Se o Web Recovery não aparece porque APPSBL, MIBIB, rede ou NAND falham antes dele, um FIT via navegador não tem onde executar. Nessa condição, a recuperação requer acesso de baixo nível, como UART quando o bootloader ainda responde, ou gravação física/programador se o bootloader não inicia.

## Verificações pendentes antes de produzir um pacote de recovery

- Extrair o payload UBI do FIT v27 e recalcular seus CRC32 e SHA-256; manter a imagem OEM original intacta.
- Montar um FIT candidato offline com a mesma estrutura/marcador aceitos pelo Web Recovery e inspecionar que o script nomeia apenas `rootfs_1` como destino de dados.
- Validar em bancada que os comandos NAND montados pela rotina usam o offset/tamanho previstos para `rootfs_1` na MIBIB carregada, inclusive quando há bad blocks.
- Validar em teste controlado o resultado do upload, leitura posterior e boot; somente então chamar o pacote de resgate funcional.
