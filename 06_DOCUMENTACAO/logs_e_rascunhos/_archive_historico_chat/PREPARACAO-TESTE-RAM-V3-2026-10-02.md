# Preparação do teste em RAM v3 — 2026-10-02

## Resultado e limite atual

Preparação offline concluída: kernel ARM64 6.18.52 recompilado com initramfs de diagnóstico, sete corretivos de Ethernet e uma sonda separada de comunicação com o U-Boot OEM. Nenhum acesso ao roteador, upload, teste no aparelho, alteração de rede/firewall, gravação de partição ou reinicialização foi feito nesta preparação.

O usuário informou acesso em 192.168.73.2. Isso não confirma qual slot está ativo nem a saúde atual do aparelho. O aviso antes de qualquer teste continua obrigatório. Os manifestos permanecem hardware_ready=false. A imagem é um diagnóstico mínimo, não uma release completa do OpenWrt e não um instalador.

## Artefatos e compilação

- Candidato: artefatos/t7-net-20261002-v3/t7-arm64-diag-CANDIDATO-NAO-ENVIAR.itb.
- Tamanho FIT: 3.503.744 bytes (aproximadamente 3,34 MiB).
- SHA-256 FIT: 0d5a9205cfdcafc34004ed8dc94973a54c1e0c367db8efac4177026ff2caaed9.
- Kernel descompactado: 11.321.352 bytes; extensão de memória declarada pelo cabeçalho ARM64: 11.665.408 bytes.
- Carga candidata: 0x41000000; fim declarado: 0x41b20000. Ainda depende do mapa real de RAM do bootloader.
- Ferramenta de compilação: ferramentas/compilar_rede_v3.sh; preparação isolada: ferramentas/preparar_kernel_v3.py.
- Scratch WSL: /home/builder/t7-chatgpt-work-20261002-v3/linux. Fontes e configurações originais preservadas.
- Fonte base: árvore local Linux 6.18.52 já modificada; não se trata de upstream puro.
- GCC 14.4.0 AArch64/musl; fontes do diagnóstico, config, vmlinux, System.map, DTB, CPIO e fontes compactadas preservados na pasta de artefatos.

Os patches GL.iNet 0371, 0372, 0374, 0375, 0376 e 0410, mais o ImmortalWrt 0362, corrigem fila TX, sincronização de parada/retomada, tabelas de escalonamento e buffers IPQ5332, uso de skb liberado e direção/limpeza do DMA RX. Foram aplicados somente na cópia isolada, com dry-run e sem fuzz. Referências fixas: GL.iNet 2365932733ca8ec3b346621d9cec2eb3df3b2cf3 e ImmortalWrt 5233c153ef7f119c567b54a92feea6919b167e84. patches-aplicados.json registra arquivos e hashes. Patches GL sobrepostos de RX não foram duplicados.

A primeira compilação falhou porque um filtro de cópia omitiu include/asm-generic/vmlinux.lds.h. O filtro foi corrigido e os arquivos de fonte restaurados na cópia. O log inicial foi preservado. A compilação final passou: logs/compilacao-rede-v3-reparo-copia.log.

## Proteção e limites do diagnóstico

O kernel incorpora /init ARM64 estático e drivers Ethernet/netconsole. MTD, módulos, /dev/mem, QFPROM, MMC, SCSI, PCI, USB, wireless e remoteproc estão desativados. Não há shell, sysupgrade ou montagem de RootFS NAND no initramfs. Isso reduz as possibilidades de gravação pelo Linux de diagnóstico; não valida automaticamente a segurança do caminho executado pelo U-Boot OEM.

RAM no DTS: referência conservadora de 512 MiB, com reservas OEM preservadas. Ramoops está compilado, mas sem região ativa: não se promete persistência de logs após reset. O endereço antigo 0x4cc00000 não foi reutilizado. O watchdog depende da inicialização do driver; a configuração não prova que o sistema sobreviverá até esse momento. Topologia PHY, portas Acer e comunicação do bootloader com TrustZone continuam sem validação no aparelho.

## Verificações concluídas

verificacao-offline.json registra sucesso para FIT, descompressão, cabeçalho ARM64, DTB, init estático, CPIO, configurações e identidade incorporada. Testes locais adicionais: quatro de identidade UDP, oito do protocolo TFTP/checkpoints e quatro da sonda; 16 verificações passaram, sem sockets ou hardware. Log: logs/validacao-local-v3-20261002.log.

O preflight do PC conferiu oito arquivos contra SHA-256 e consultou adaptador/endereço/listeners sem contactar o roteador. Evidência: evidencias/preflight-v3-20261002-221612.json. Naquele instante Ethernet 4 estava UP, ifIndex 15, com 192.168.1.5 e 192.168.73.5, entre outros IPv4 /24. Nenhum listener UDP 69/6666/6667 foi encontrado. 169.254.73.1 ainda não estava configurado. Esses dados são uma fotografia, não garantia para um teste posterior.

## Roteiro antes de tocar no aparelho

1. Avisar o usuário antes da etapa com hardware. Confirmar se 192.168.73.2 é o Acer T7 e identificar o slot ativo e o caminho de recuperação. ferramentas/inventario_roteador_somente_leitura.sh foi preparado para inventário, mas não executado. A identificação deve cruzar /proc/mtd, sysfs UBI e montagem de raiz; índices ubi0/ubi1 ou primaryboot isoladamente não provam o slot físico.
2. Confirmar cabo LAN 1 do T7/Ethernet 4 do PC e repetir apenas o preflight local quando necessário. O PC também tem outra interface na rede 192.168.73.x; uma sessão de diagnóstico nessa rede deverá usar explicitamente a interface/origem correta. Não alterar rotas automaticamente.
3. Confirmar que o método de recuperação conhecido está utilizável e que os artefatos de retorno são os corretos. A recuperação relatada pelo usuário não foi exercitada nesta preparação.
4. Validar o contexto de execução HTTP/source do U-Boot atual antes de liberar a sonda. Os flags de liberação devem refletir evidência real; não preencher true apenas para contornar bloqueios dos scripts.

## Primeiro teste proposto: sonda do U-Boot, sem kernel

Pasta: artefatos/sonda-uboot-rede-30fa04acf23b48a7a705e5455ae728a0.

O arquivo sonda.itb.PENDING contém somente um script com variáveis temporárias de rede e tftpput de 64 bytes já existentes no início do buffer de upload 0x44000000. Não baixa kernel, não executa bootm, não chama saveenv e não contém comandos de gravação de flash. O marcador Flas no offset 0x5c foi conservado para a classificação de script identificada no firmware analisado. A aceitação pelo firmware atual ainda precisa ser demonstrada.

O receptor ferramentas/receber_sonda_uboot.py exige a sessão, IP de origem, nome de arquivo e os 64 bytes esperados. Um pacote aleatório, serviço OEM acessível ou cabeçalho incorreto não contam como sucesso. O receptor recusa execução enquanto faltarem flags de hardware, slot, link e recuperação. Sem --executar, apenas valida os arquivos locais.

Esse teste pode interromper o serviço e provocar reset quando o handler OEM retorna. Não chamar de risco zero. Receber o cabeçalho exato comprova apenas execução da sonda e retorno TFTP pelo U-Boot; não comprova execução do Linux nem libera os outros endereços RAM.

## Segundo teste: carregar e conferir em RAM, ainda sem bootm

Depois da sonda, validar a semântica real dos comandos, tamanho/CRC do FIT recebido, comportamento de autostart, cópia do script, áreas temporárias, heap/stack/global data e fixups/posicionamento do DTB. Os candidatos 0x44000000 (HTTP), 0x45000000 (checkpoint) e 0x46000000 (FIT recebido) não estão aprovados. O gerador existente de verificação deve continuar bloqueado enquanto faltar essa evidência. Não existe acionador de boot v3 liberado.

Uma imagem FIT comum enviada ao HTTP Failsafe pode ser interpretada como firmware a gravar. Portanto, não enviar o candidato diretamente à interface de recuperação. Antes de qualquer execução, revisar o ramo OEM que receberá o arquivo, além do conteúdo do script.

## Terceiro teste: boot diagnóstico ARM64

Somente após as duas etapas anteriores: preparar a recepção Windows na Ethernet correta, configurar 169.254.73.1 de forma temporária e reversível, avaliar as regras de firewall necessárias e iniciar a coleta antes do salto. Não usar WSL NAT como receptor externo sem validar o caminho. Nada disso foi configurado nesta etapa.

Critério positivo: pacote T7NET1 com identidade 30712cb0064047b6b603bf562d069c4e, build t7-net-20261002-v3, arquitetura aarch64, kernel 6.18.52-t7-net-20261002-v3, boot_id válido e evento INIT_REACHED. Registrar também sequência e mensagens recebidas. Netconsole na UDP 6667 fornece mensagens depois de a rede estar utilizável; identidade na UDP 6666 identifica o init correto.

Ausência de pacote não prova bloqueio EL3: PHY, rede, watchdog, DTB, fixups e falhas anteriores à rede continuam causas possíveis. Ping ou LuCI em 192.168.73.2 pode ser o firmware OEM após retorno e não é prova do kernel novo. A sonda usa 192.168.1.1/192.168.1.5; o diagnóstico Linux usa 169.254.73.x, portanto os dois estágios não devem ser confundidos.

## Depois de eventual sucesso

O próximo produto seria um OpenWrt initramfs completo com shell/SSH e diagnóstico controlado. Só depois de verificar hardware, NAND/UBI e identidade física dos volumes considerar uma imagem persistente no Slot 2. Slot 1, bootloader, TrustZone, ambiente persistente e partições compartilhadas ficam fora dos destinos de gravação dessa estratégia. Nenhuma instalação está preparada ou autorizada por este documento.

## Estado para outra IA

Leia este documento, sessao-teste-v3-PENDENTE.json, manifesto-candidato.json e verificacao-offline.json antes de qualquer comando. v1/v2 e relatórios anteriores são histórico preservado. A anotação anterior de que v3 ainda não estava compilado foi superada por esta preparação. Não converter hipótese de falha ARM64 em diagnóstico conclusivo. Nenhum teste no aparelho foi realizado aqui.
