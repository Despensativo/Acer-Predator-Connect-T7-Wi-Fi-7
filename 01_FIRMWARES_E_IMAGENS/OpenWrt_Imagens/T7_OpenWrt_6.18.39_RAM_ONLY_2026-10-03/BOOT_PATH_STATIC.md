# T7: caminho de boot ARM64 e próximo teste

Data: 2026-10-03. Análise estática local, sem contato com o roteador e sem executar o APPSBL.

## Fatos observados no APPSBL Acer

Origem: `02_BACKUPS_E_DUMPS/MTD_Full_Dumps/appsbl.bin`, 1.572.864 bytes, SHA-256 `3d6281190512ba50b83eea1a2d6fca69f01da5bb390d52b601e762ce8f1df2fc`. ELF AArch32, segmento PT_LOAD em offset `0x12000`, mapeado em `0x4a400000`.

- Em `0x4a402168`, a rotina lê o word no offset `0x38` da entrada do kernel; em `0x4a40216c`, compara com o literal `0x644d5241` (magic ARM64, bytes `ARMd`).
- Se coincidir, `0x4a402176` chama `0x4a401bbc` com endereço de entrada e FDT.
- Essa rotina constrói os parâmetros de salto e chama a ponte SCM em `0x4a401c0c`; a instrução `smc #0` está em `0x4a401a7c`, no caminho chamado. A mensagem `Jumping to AARCH64 kernel via monitor` aparece no binário no offset de arquivo 448861, referenciada pela rotina.
- Isso confirma um caminho AArch32 → monitor seguro → kernel AArch64 no código do APPSBL Acer. A funcionalidade no aparelho e a aceitação de nosso FIT continuam sem teste.

## Candidato OpenWrt 6.18.39

FIT final: 8.305.020 bytes, SHA-256 `04fb7b7075a3bbec524dddc969aa8ac941aade27ffb4142c39e7586fc341fc8d`. O payload LZMA do kernel descomprime para 27.656.200 bytes. Seu cabeçalho ARM64 declara `text_offset=0`, `image_size=0x1ac0000` (28.049.408 bytes) e magic `ARMd`.

**Inferência:** se carregado em `0x46000000`, o FIT termina antes de `0x47000000`; o kernel descomprimido em `0x41000000` termina em `0x42ac0000`. Não há sobreposição entre esses intervalos nem com o upload HTTP planejado em `0x44000000`. Todos cabem abaixo de `0x60000000`, o limite do DTB genérico de 512 MiB. Isso é aritmética estática, não validação da RAM livre, da relocação do FDT ou dos buffers do U-Boot no aparelho.

## Caminho de lançamento identificado

A análise anterior de `BOOT-RAM-TFTP-VERIFICACAO-2026-10-02.md` encontrou no APPSBL os comandos `source`, `tftpboot` e `bootm`, e o ramo do recuperador HTTP que seleciona scripts FIT pelo marcador `Flas` no offset `0x5c`. Esse ramo usa `sf probe; imgaddr=0x%lx && source $imgaddr:script`. O arquivo kernel FIT não deve ser enviado diretamente à página HTTP: outros tipos de upload seguem caminhos de gravação da flash.

A sonda já preparada em `07_ARTEFATOS_BUILD_WSL/artefatos/sonda-uboot-rede-30fa04acf23b48a7a705e5455ae728a0/sonda.itb.PENDING` tem 33.582 bytes, SHA-256 `66a25b2d44a9c80732193b138bdaba7ea6234978f5734e3dca6d54b779c556d8` e marcador `Flas`. Seu script só define IPs voláteis e solicita por `tftpput` o retorno de 64 bytes do buffer do próprio upload. Não contém `bootm`, download de kernel, `saveenv` nem comandos de gravação. **Precisa confirmar:** se o handler HTTP atual executa o script e se o U-Boot alcança a rede. Um upload pode reiniciar o aparelho ao retornar do handler.

O candidato diagnóstico v3 já existente (`t7-net-20261002-v3`) tem 3.503.744 bytes, kernel 6.18.52, initramfs mínimo sem MTD/shell e correções de Ethernet. Ele é mais adequado ao primeiro teste ARM64 que o OpenWrt completo 6.18.39, mas ainda depende da sonda e do mapa dinâmico de RAM. Ambos continuam sem boot comprovado.

## Sequência antes de executar no hardware

1. Confirmar estado atual do T7, slot ativo e caminho real de recuperação; documentar como observar o resultado. UART 3,3 V, se acessível, é o meio mais direto de ver erro do `source`, do `bootm` ou do kernel.
2. Revalidar o PC, a interface física e os hashes. Obter autorização específica antes de colocar o aparelho em Failsafe ou enviar a sonda, conforme a instrução anterior do usuário de avisar antes do teste.
3. Testar primeiro a sonda sem kernel. Exigir o retorno exato de 64 bytes e registrar reset/retorno ao OEM. Um simples HTTP 200 ou log de TFTP não basta.
4. Só depois validar o carregamento, tamanho, CRC, `autostart`, mapa de RAM e fixups do FDT com o acionador de verificação, ainda sem `bootm`.
5. Com essas verificações, preparar e revisar acionador de boot em RAM. Não gravar NAND, não alterar ambiente persistente e não atualizar U-Boot para resolver a passagem 32→64.

Limite atual: não existe acionador de boot liberado. O projeto já contém uma sonda `.PENDING`; seu envio ou qualquer teste no T7 não ocorreu nesta etapa.

Preflight local do PC em 2026-10-03: `Ethernet 4` está UP, mas usa `192.168.73.181/24`; não há `192.168.1.5` nessa interface. A sonda preparada especifica `serverip=192.168.1.5`. Nenhuma configuração de rede foi alterada e nenhum pacote foi enviado ao roteador. Antes do ensaio, conferir a topologia atual e planejar alteração temporária e reversível do IPv4 do PC.
