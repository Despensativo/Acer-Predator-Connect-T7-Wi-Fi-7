# Verificacao offline da configuracao existente

Data: 2026-10-02. Nenhum acesso ao roteador, compilacao ou instalacao.

## Fato observado

O verificador foi executado contra um instantaneo da configuracao do Linux 6.18.52 presente no WSL. Dos requisitos examinados, dez ficaram divergentes ou nao confirmados: sete divergencias explicitas e tres simbolos ausentes.

| Simbolo | Esperado no diagnostico | Configuracao existente |
| --- | --- | --- |
| CONFIG_DEVTMPFS | y | n |
| CONFIG_PSTORE | y | n |
| CONFIG_PSTORE_RAM | y | ausente |
| CONFIG_PSTORE_CONSOLE | y | ausente |
| CONFIG_MTD | n | y |
| CONFIG_MODULES | n | y |
| CONFIG_PSTORE_BLK | n | ausente |
| CONFIG_MMC | n | y |
| CONFIG_SCSI | n | y |
| CONFIG_NVMEM_SYSFS | n | y |

A ausencia das opcoes filhas de PSTORE e compativel com o subsistema principal desativado. Ela nao prova, isoladamente, que os simbolos nao existem no Kconfig. O verificador mantem essas entradas como nao confirmadas.

O codigo de saida 1 foi esperado: indica que a configuracao examinada nao atende integralmente aos requisitos. Nao representa falha de leitura do arquivo.

## Inferencia

A configuracao existente ainda nao e a configuracao minima proposta para diagnostico sem acesso normal a flash. Alem de faltar PSTORE, ela inclui MTD e carregamento de modulos. Portanto, reutilizar esse kernel nao implementa as protecoes da especificacao.

CONFIG_DEVTMPFS=n requer revisar como /dev seria criado pelo initramfs. A especificacao pede DEVTMPFS para reduzir dependencias e tornar o init minimo explicito; sua ausencia nao prova, sozinha, que todo boot falharia.

## Precisa confirmar

- Correspondencia entre este .config e cada imagem final antiga; esta verificacao nao abriu ELFs/FITs.
- Conteudo e comportamento do initramfs.
- Requisitos e dependencias reais no Kconfig antes de preparar uma nova configuracao.
- Mapa dinamico de RAM, posicionamento do DTB, watchdog e caminho de observacao do kernel.

## Evidencias locais

- [Instantaneo da configuracao](evidencias/kernel-config-2026-10-02.txt)
- [Resultado JSON](evidencias/verificacao-config-2026-10-02.json)
- [Verificador offline](validar_config_diagnostico.py)

Nenhum novo ITB foi produzido. Nenhum arquivo foi liberado para upload.
