# Alternador de boot T7 V2 para Web Recovery

**Estado:** FITs `.bin` gerados e verificados offline em 10/10/2026. O usuário preferiu deixar o teste no U-Boot para depois; o V2 **não foi enviado ao T7**. Os alternadores V1 em `../Alternador_Boot_T7/` permanecem intactos.

| Arquivo final para upload | Slot selecionado | SHA-256 | Tamanho |
|---|---:|---|---:|
| `selecionar_slot1_V2_CANDIDATO.bin` | 1 (`primaryboot=1`) | `3bfb8f6eff8bb1f9b432a69eb4d474a13ce14de3162a8248896a452f27ef873e` | 2.622.847 bytes |
| `selecionar_slot2_V2_CANDIDATO.bin` | 2 (`primaryboot=0`) | `4214cd812351225a2d4285db88a04a297c7677952c8e95c0b2501baa3b6d9c9d` | 2.622.847 bytes |

Os `.bin` são **FITs de U-Boot**, não dumps raw, apesar da extensão. Cada FIT contém `script`, `bootconfig` integral de 512 KiB e um payload de preenchimento de 2 MiB para o upload do Web Recovery. O preenchimento não é gravado. As imagens de BOOTCONFIG vieram do backup do T7 em `../Teste_Selecao_Nativa_Slot2/` e diferem somente no byte `0x6c`: `1` para o Slot 1 e `0` para o Slot 2.

## Diferença em relação ao V1

O script V2 inicializa a NAND, extrai `bootconfig`, grava `0:BOOTCONFIG` e `0:BOOTCONFIG1`, relê cada área física de 512 KiB e compara com o payload antes de chamar `reset`. Ele **não** executa `setenv`, `saveenv` nem define `fsbootargs`. Não grava `APPSBLENV`, `rootfs`, `rootfs_1`, `MIBIB`, `ART`, kernel ou firmware Wi-Fi. O V1 persistia `fsbootargs=ubi.mtd=rootfs_1` para o Slot 2; essa configuração não estava presente no teste que conseguiu iniciar a stock v27 no Slot 2.

O V2 pressupõe `fsbootargs` ausente no ambiente persistente antes do envio. Em 10/10, a leitura ao vivo no Slot 2 mostrou a variável ausente, `BOOTCONFIG` e `BOOTCONFIG1` com SHA-256 `e2f66a844a76c6e1bf5e80c855905a09b4ec259a9a5fa00fe628b87db59db163`, e `APPSBLENV` com SHA-256 `401868806b88348a965b781579f2f566710836f8acf35aff3433fce70a49f613`. Se `fsbootargs` tiver sido definida em outro ensaio, estes FITs não a removem. O alternador V1 de retorno ao Slot 1 limpa essa variável e continua preservado.

## Teste inicial proposto

1. Com o **Slot 2 já ativo e funcional**, entrar no Web Recovery com WPS ao ligar. Isso permite testar o FIT V2 do Slot 2 sem trocar a partição selecionada antes do ensaio.
2. Enviar **somente** `selecionar_slot2_V2_CANDIDATO.bin` ao Web Recovery. Não enviar as imagens `RAW_NAO_WEB.bin` dessa pasta de origem.
3. Após o reset do U-Boot, conferir pelo Linux `/etc/version`, `rootfs/primaryboot` nas duas BOOTCONFIG, `fw_printenv fsbootargs`, SHA-256 de `mtd3`/`mtd4`, uptime, painel, Ethernet e rádios. O recebimento do upload sozinho não comprova execução bem-sucedida.
4. Se não houver rede, usar WPS/Web Recovery e o alternador V1 de Slot 1 preservado em `../Alternador_Boot_T7/selecionar_slot1_CANDIDATO.bin`.

Esse ensaio valida o caminho Web Recovery do V2 mantendo o Slot 2 selecionado. Um teste real de **troca** de Slot 1 para Slot 2 ainda requer voltar ao Slot 1 e repetir a seleção. O script gerador `gerar_alternadores_v2.py` apenas constrói os arquivos offline; não se conecta ao roteador.
