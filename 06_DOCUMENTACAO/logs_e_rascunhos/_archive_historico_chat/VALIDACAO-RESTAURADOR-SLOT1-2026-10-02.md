# Validação do restaurar_slot1_acer.itb — 2026-10-02

Escopo: inspeção offline do arquivo fornecido no Desktop. Nenhum upload, execução ou gravação no roteador. Original preservado; cópia auditada e script extraído em artefatos/recuperacao-slot1-auditada-20261002.

## Conclusão

FIT íntegro e compatível com o marcador de script do handler OEM previamente analisado. Script e payload bootconfig têm CRC32 correto. O payload de 524.288 bytes é idêntico aos dois backups locais backup_predator_t7_bootconfig.bin e backup_predator_t7_bootconfig1.bin. Comparado ao backup Slot 2, só difere no byte 0x6c: valor 1 no original/retorno e 0 no Slot 2. Isso sustenta a intenção de retornar à seleção original, mas não demonstra sucesso no aparelho atual.

Não é uma restauração de todo o firmware de fábrica: não contém kernel nem RootFS. É uma alteração persistente de ambiente e de duas cópias da configuração de boot, seguida de reset. A mensagem impressa de “100% original” excede o que o script faz; alterações existentes no sistema/overlay não são revertidas.

## Comandos e impacto

- setenv fsbootargs: remove a variável.
- setenv bootargs console=ttyMSM0,115200n8: substitui os argumentos nessa variável.
- setenv bootcmd bootipq e saveenv: grava o ambiente persistente.
- imxtract: extrai bootconfig do FIT em RAM 0x45000000.
- mw.b 0x4500006c 0x01: ajusta seleção; o byte já é 1 no payload fornecido.
- nand device 0; erase/write de 0x80000 bytes em 0x400000 e 0x480000: apaga e regrava as duas áreas de bootconfig presumidas.
- reset: reinicia.

Os destinos são compatíveis com o layout histórico do projeto (BOOTCONFIG/BOOTCONFIG1), mas não houve leitura da tabela atual/MIBIB nem validação da seleção NAND neste aparelho. O script não contém destinos explícitos de escrita para kernel, RootFS, QSEE, ART ou APPSBL, mas trabalha com offsets físicos e altera estruturas de seleção compartilhadas. A ausência desses destinos não autoriza chamar o procedimento de risco zero.

## Falha de proteção encontrada

Os comandos estão em sequência sem if/then para checar extração, seleção de NAND, erase, write ou saveenv. Não há releitura/verificação depois das gravações. Se imxtract falhar, os comandos seguintes ainda podem operar com RAM inválida; se a primeira gravação falhar, a segunda ainda pode ser tentada. Ambas as cópias são regravadas no mesmo procedimento. Isso impede classificar o arquivo como recuperação robusta com garantia de sucesso.

## Decisão para o teste em RAM

Guardar como artefato de recuperação histórico validado quanto a estrutura/conteúdo, sem enviá-lo agora. A sonda de comunicação não deve chamar esse arquivo nem incluir suas gravações. Primeiro confirmar o estado atual e se um reboot normal retorna ao sistema funcional, antes de depender de uma restauração que grava as duas cópias de bootconfig. Qualquer aplicação deste restaurador exige aviso e revisão do alvo; nesta etapa foi autorizado apenas validar.

SHA-256: 2908bb3e8d498c0fda728c935c5d13f32f9484b3996e9df7d5f06439ba16828e.
