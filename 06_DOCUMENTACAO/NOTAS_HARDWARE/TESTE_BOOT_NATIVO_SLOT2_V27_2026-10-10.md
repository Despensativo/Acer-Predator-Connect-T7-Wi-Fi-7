# Teste de seleção nativa do Slot 2 — stock v27 — 10/10/2026

## Alteração realizada

Com o T7 inicialmente no Slot 1, foi salva uma cópia integral de `BOOTCONFIG` (`mtd3`), `BOOTCONFIG1` (`mtd4`), `APPSBLENV` (`mtd13`) e `SYSTRACE` (`mtd23`) em `_FORA DO GitHub/Backups_teste_boot_nativo_slot2_2026-10-10/`. As duas BOOTCONFIG tinham `rootfs/primaryboot=1` e `upgradepartition=rootfs_1`.

Foi criada uma imagem de BOOTCONFIG de 512 KiB alterando somente o byte em `0x6c`, de `1` para `0`, para selecionar a partição de atualização. O arquivo de origem e o arquivo alterado estão em `04_SCRIPTS_E_FERRAMENTAS/Teste_Selecao_Nativa_Slot2/`. O script `aplicar_no_linux_t7.sh` validou as pré-condições e os SHA-256, gravou a imagem integral em `mtd3` e `mtd4` e leu ambas de volta. O SHA-256 lido das duas partições foi `e2f66a844a76c6e1bf5e80c855905a09b4ec259a9a5fa00fe628b87db59db163`, igual ao arquivo de destino. `APPSBLENV` e a UBI não foram gravados; `fsbootargs` continuou inexistente. Um reboot foi então solicitado.

Os arquivos `*.bin` desse teste são imagens **raw de partição**, não FITs de Web Recovery. O alternador anterior para o Slot 1 foi preservado: `04_SCRIPTS_E_FERRAMENTAS/Alternador_Boot_T7/selecionar_slot1_CANDIDATO.bin`.

## Resultado observado

- O painel abriu pela rede após o reboot. A rede caiu cerca de 34 segundos depois, permaneceu indisponível por aproximadamente um minuto e voltou. O motivo desse novo boot não foi identificado; não atribuir a queda a um componente específico sem mais evidência.
- Após o retorno, `/etc/version` mostrou `T7_BR_1.01.000027` e as duas BOOTCONFIG mostraram `rootfs/primaryboot=0`.
- Os nomes MTD apresentados ao Linux trocaram de lugar: no sistema iniciado, `rootfs=mtd20` (endereço `0x01640000`) e `rootfs_1=mtd21` (endereço `0x10640000`); antes do teste, `rootfs_1=mtd20` e `rootfs=mtd21`. O UBI ativo está anexado a `mtd20`. Assim, `ubi.mtd=rootfs` é o nome lógico do sistema escolhido e, sozinho, não distingue os dois boots. A combinação de nome/endereço MTD, BOOTCONFIG e versão confirma que a stock v27 gravada no **Slot 2** iniciou.
- O Telnet, painel HTTP/HTTPS e DNS responderam após o segundo boot. `ath0`, `ath1` e `ath2` estavam `UP,LOWER_UP`; `iw dev` mostrou SSIDs stock em 2,4, 5 e 6 GHz. O processo `hostapd` estava ativo. Isso confirma a subida dos rádios, não desempenho de clientes ou conexão à Internet.
- No boot observado, o log registrou carregamento de `qcn9224/amss_dualmac.bin`, `qcn9224/regdb.bin` e subida do processador `QCN9224_PCI1`. Houve parada e nova subida desse processador durante a sequência de inicialização. O trecho inspecionado não mostrou `Target hung at Post-STM` nem pânico de kernel.
- O log também contém falhas de conexão do serviço WMI DBR (`Target failed service 0x108`) e uma falha de ACS ao escolher canal. Os rádios subiram apesar dessas mensagens. Elas exigem investigação separada se houver perda de Wi-Fi; não explicam, por si, o reboot inicial.
- O SHA-256 de `SYSTRACE` permaneceu `fa77caf303e6d67b6b23c9da1f2b5ae61f00dd0fffd30c6ddb5efa2e46e29289`, igual ao backup pré-teste. Portanto, essa partição não capturou um novo diagnóstico da queda de rede.
- A checagem contínua após a volta mostrou uptime crescente de 108 a 320 segundos, sempre na v27, sem novo reboot nesse intervalo. Estabilidade por horas ou dias ainda não foi medida.

## Limite da conclusão

O teste confirma que a seleção com BOOTCONFIG integral e sem `fsbootargs` consegue iniciar a stock v27 no Slot 2, com rede e rádios. Nas três tentativas anteriores que falharam, a BOOTCONFIG foi exportada de `/proc/boot_info` em arquivos de 336 bytes, e `fsbootargs` foi definido manualmente como `ubi.mtd=rootfs_1`. Portanto, este teste mudou **duas variáveis ao mesmo tempo** e não isola qual foi decisiva. O alternador FIT de Slot 2 já gerado contém uma BOOTCONFIG integral, mas não havia sido validado no aparelho; ele também define `fsbootargs` manualmente. O fato de o boot funcional apresentar a partição ativa ao Linux como `rootfs` torna `ubi.mtd=rootfs_1` suspeito nesse caminho, sem provar causalidade. Também não foi demonstrado que uma atualização completa pelo painel Acer seja necessária.

O Slot 2 foi deixado selecionado após a leitura, sem novas gravações. Para um retorno ao Slot 1, usar o alternador preservado via WPS/Web Recovery ou restaurar, pelo Linux, as imagens raw originais de `mtd3` e `mtd4` com verificação de leitura, conforme o estado da rede.
