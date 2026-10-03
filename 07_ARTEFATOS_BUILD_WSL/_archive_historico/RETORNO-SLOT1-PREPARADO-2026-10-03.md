# Retorno ao Slot 1 — preparação de 03/10/2026

## Resultado

Backups atuais e um candidato de recuperação foram preparados. Nenhum arquivo foi enviado ao Failsafe, nenhuma seleção de slot foi alterada, nenhuma flash foi gravada e nenhum reinício foi solicitado nesta etapa. O candidato permanece **NÃO ENVIAR**, com hardware_ready=false e upload_authorized=false.

O propósito é permitir futuramente selecionar novamente o Slot 1 pelo Failsafe em 192.168.1.1. A existência da página não comprova que o script de retorno será executado corretamente. Também não foi comprovado retorno automático após falha no Slot 2.

## Fatos observados

O último estado verificado era Slot 1 ativo em 192.168.73.2: rootfs/mtd21, ubi0, Linux OEM 5.4.213 armv7l. O Slot 2 é rootfs_1/mtd20 e permanece sem teste de boot nesta frente. A conferência anterior mostrou kernel, RootFS e wifi_fw iguais aos do Slot 1 e overlay sem blocos associados; não há motivo demonstrado para regravar esses volumes.

Backups coletados por comandos somente de leitura via Telnet, salvos em `artefatos/retorno-slot1-20261003T030556Z`:

| Arquivo | Bytes | SHA-256 |
| --- | ---: | --- |
| BOOTCONFIG.bin e BOOTCONFIG1.bin | 524288 cada | bcb6b37e13b0231ce735f31705ecd97dde563a35c2605c0de467a77c35d56ebe |
| APPSBLENV.bin | 524288 | d7e52fec81fb28141cfde02e08cbade5af0df8eb3b1b0231ea29b3d1ed710d2c |
| export-bootconfig0.bin e export-bootconfig1.bin | 336 cada | 06224a641ca940cc6c59b33108552ae29264eb077c680df3e0a95a6036890e36 |

As duas cópias brutas de BOOTCONFIG são iguais e indicam primaryboot=1 no campo conferido em 0x6c. As duas exportações também são iguais. Contudo, comparando os primeiros 336 bytes da flash com a exportação proc, há diferença em 0x04: flash=2, exportação=3. **Não substituir silenciosamente os formatos.** A hipótese de contador de geração ainda exige validação da implementação e de como o bootloader escolhe a cópia.

O CRC do ambiente é válido para uma estrutura de 262144 bytes, com CRC little-endian nos primeiros quatro bytes e dados entre 4 e 262143. A partição inteira tem 524288 bytes. Os testes históricos sobre a partição inteira estão identificados no manifesto como geometria incorreta; não indicam corrupção do ambiente.

Variáveis de seleção observadas: bootcmd=bootipq, bootargs=console=ttyMSM0,115200n8, fsbootargs ausente. Endereços persistentes ipaddr=192.168.10.1 e serverip=192.168.10.10 não demonstram os endereços usados durante o Failsafe HTTP. O backup do ambiente pode conter dados privados e deve permanecer local.

## Candidato offline

Gerador: `ferramentas/gerar_retorno_slot1_verificado.py`.

Arquivo: `artefatos/retorno-slot1-20261003T030556Z/retornar-slot1-CANDIDATO-NAO-ENVIAR.itb`.

Tamanho: 1052470 bytes. SHA-256: 5497c05738700541aff659d5ba01c4fbb096bdd21df448c1d4421b7ff22aa8e5.

Contém os dois backups brutos, um script e hashes CRC32. O marcador Flas em 0x5c foi conferido conforme a análise estática do classificador HTTP OEM. Isso não é validação dinâmica nem autorização de upload.

Se executado, o script pretende:

1. Extrair cada backup para RAM e conferir tamanho e bytes antes das escritas.
2. Selecionar NAND 0, apagar/gravar BOOTCONFIG em 0x400000 e BOOTCONFIG1 em 0x480000, com 0x80000 bytes por cópia.
3. Ler novamente cada cópia e comparar contra o payload original do FIT.
4. Remover fsbootargs, restaurar bootcmd/bootargs de seleção e executar saveenv.
5. Solicitar reset somente após todos os passos anteriores retornarem sucesso.

**Escreve estruturas compartilhadas de inicialização e ambiente**, embora não contenha comandos de gravação de kernel, RootFS ou overlay. Essas três operações persistentes não são atômicas. Não restaura a partição APPSBLENV inteira: apenas as variáveis indicadas, por saveenv. Endereços de RAM 0x44000000/0x45000000 ainda não foram aprovados por teste dinâmico.

## Validação e limites

Hashes dos backups, CRC do ambiente na geometria correta, estrutura FIT, CRC32 dos três payloads, marcador OEM, endereços dos payloads após empacotamento e script LF foram verificados localmente. Trinta simulações em Bash passaram: sucesso completo e falha individual em cada uma das 29 operações controladas. Nas falhas simuladas, o script termina e não chama seu reset nem continua para a operação seguinte.

A simulação usa comandos falsos; **não valida o interpretador hush OEM, NAND, tratamento de bad blocks, imxtract/filesize ou comandos cmp/itest reais**. O próprio handler HTTP OEM pode reiniciar após o término do script, inclusive em caso de erro. Portanto, o teste não garante ausência de reinício físico nem restauração em qualquer circunstância.

Os comandos necessários foram encontrados no dump do U-Boot. A sonda de comunicação anteriormente enviada não retornou o cabeçalho esperado: a execução por source via HTTP continua sem confirmação. Uma tela de upload concluído não prova execução do script.

## Próxima etapa proposta, ainda não executada

Antes de chavear o Slot 2, resolver a diferença de geração das BOOTCONFIG e confirmar o caminho de execução HTTP com uma sonda sem escrita persistente. Capturar ARP/TFTP na Ethernet 4 durante essa sonda ajuda a distinguir ausência de execução, endereço inesperado e falha de comunicação. Avisar o usuário antes desse teste.

Só depois dessas validações e de um roteiro de retorno confirmado, testar a seleção do Slot 2 OEM. O sucesso exige verificar rootfs_1, UBI associado a mtd20 e sistema operacional funcionando; acesso ao IP, isoladamente, não prova o slot. Ao retornar ao Slot 1, confirmar rootfs/mtd21, UBI e serviços em 192.168.73.2.

Evidências locais: backup-manifesto.json, recuperacao-manifesto-PENDENTE.json, verificacao-local-adicional.json, diferencas-bootconfig-flash-vs-export.json, retorno-script.txt, retorno.its e teste-fluxo-simulado.sh na pasta indicada. O último arquivo só contém comandos simulados para execução local.
