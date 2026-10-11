# Seleção do Slot 2: mecanismo confirmado e teste recomendado — 2026-10-02

Consulta remota somente leitura autorizada no contexto do planejamento. Nenhum comando de chaveamento executado, escrita ou reinício enviado.

## Fatos atuais

Foram lidos /usr/sbin/boot-openwrt e /usr/sbin/boot-acer no aparelho. bootconfig0/rootfs/primaryboot e bootconfig1/rootfs/primaryboot retornaram 1. fsbootargs não retornou valor; bootcmd=bootipq e bootargs=console=ttyMSM0,115200n8. Cruzamento anterior confirmou Slot 1=rootfs/mtd21 ativo e Slot 2=rootfs_1/mtd20 inativo.

boot-openwrt faz fw_setenv fsbootargs para ubi.mtd=rootfs_1 root=mtd:ubi_rootfs rootfstype=squashfs, define primaryboot=0 nos dois objetos proc, exporta getbinary_bootconfig para /tmp, desbloqueia mtd3/mtd4 e apaga/regrava ambas as BOOTCONFIG, depois reboot. boot-acer remove fsbootargs, define primaryboot=1, exporta/grava ambas e reboot.

Os nomes desses comandos não indicam boot em RAM: alteram ambiente e seleção persistentes. Os scripts seguem em sequência sem checagens explícitas de sucesso, sem releitura/verificação após mtd write e sem abortar antes do reboot se uma gravação falhar. Não executá-los cegamente como ensaio sem risco.

## Melhor próximo teste

Usar o kernel OEM 5.4 já idêntico entre os slots para isolar a seleção/boot do Slot 2. Não regravar kernel, RootFS, wifi_fw ou esvaziar novamente overlay.

Antes de chavear: salvar cópias atuais de APPSBLENV/BOOTCONFIG/BOOTCONFIG1 e seus hashes no PC; confirmar exports, comprimentos e tabela atual de partições; preparar e revisar a configuração proposta sem gravá-la. Verificar que a alteração de bootconfig se limita ao campo rootfs esperado, conservando os demais campos. Planejar restauração usando o estado atual salvo, não apenas backup antigo.

Se optar por chaveamento persistente: usar procedimento com validação de cada operação, conferência da releitura de ambiente e bootconfig antes do reboot e interrupção em qualquer falha. Considerar explicitamente a falta de atomicidade entre as duas cópias e o efeito de eventual queda de energia. A sequência exata de escrita precisa de revisão específica do mecanismo de redundância; este relatório não libera uma implementação nova.

Avisar antes da troca e da indisponibilidade. Monitorar a rede e guardar a captura. IP acessível não prova slot: sucesso exige bootargs ubi.mtd=rootfs_1, UBI vinculado a mtd20, raiz/overlay correspondentes e inicialização funcional. Overlay vazio pode reconstruir configurações e alterar IP/acesso; não presumir que continuará em 192.168.73.2 ou que haverá LuCI/comandos personalizados herdados do overlay. Não prometer retorno automático: ele não foi demonstrado.

O caminho sem escrita persistente seria um boot específico em RAM para carregar o volume do Slot 2 com ambiente volátil, mas depende de validar comandos e mapa RAM do U-Boot, atualmente pendentes. Não improvisar esse caminho para evitar as verificações.

## Evidência

- evidencias/selecao-boot-somente-leitura-20261003T025922Z.txt.
- CONFERENCIA-SLOT2-ATUAL-2026-10-02.md.

Resultado desta etapa: mecanismo de seleção confirmado; teste de boot do Slot 2 ainda não executado.
