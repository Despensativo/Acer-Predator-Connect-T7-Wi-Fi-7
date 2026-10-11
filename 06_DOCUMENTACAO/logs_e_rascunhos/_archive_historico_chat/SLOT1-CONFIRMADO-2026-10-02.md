# Estado confirmado do Slot 1 — 2026-10-02

Consulta remota somente leitura em 192.168.73.2 após o usuário sair do Failsafe por reinicialização normal. HTTP respondeu; SSH incompatível com a biblioteca e Telnet permitiu a consulta. Nenhuma configuração alterada, partição escrita ou reinicialização enviada pelo agente.

## Fatos observados

- Linux 5.4.213, arquitetura armv7l.
- Linha de comando: ubi.mtd=rootfs, root=mtd:ubi_rootfs, rootfstype=squashfs.
- /proc/mtd: mtd21=rootfs; mtd20=rootfs_1.
- /sys/class/ubi/ubi0/mtd_num=21.
- ubi0: wifi_fw e kernel static; ubi_rootfs e rootfs_data dynamic.
- /rom: /dev/mtdblock27, SquashFS; /overlay: /dev/ubi0_3, UBIFS.
- bootcmd=bootipq. primaryboot não retornou valor na consulta; não usado para inferência.

O cruzamento bootargs/MTD/UBI/overlay confirma o sistema rodando na partição rootfs, identificada no projeto como Slot 1. O Slot 2 não apareceu anexado nessa consulta; isso não demonstra defeito nem confirma seu conteúdo.

O retorno normal Failsafe → sistema em 192.168.73.2 foi observado sem aplicar restaurar_slot1_acer.itb. Portanto o restaurador que regrava bootconfig não é necessário para este retorno já demonstrado. Isso não garante recuperação de qualquer falha futura.

## Evidências

- evidencias/inventario-slot-telnet-20261003T014259Z.txt: kernel, bootargs e tabela MTD. A captura inicial encerrou antes das seções UBI/mount; foi complementada pela consulta abaixo.
- evidencias/inventario-slot-mapa-20261003T014326Z.txt: mapa UBI/montagem e bootcmd, com terminador T7_MAP_DONE.

Aviso prévio ao teste da sonda continua necessário. Nenhum listener TFTP iniciado, upload ou teste ARM64 realizado. hardware_ready permanece false.
