# Teste completo offline do SquashFS Acer — 2026-10-02

## Resultado

O RootFS original foi completamente extraído, remontado com mksquashfs 4.2 compatível e extraído novamente. Todos os comandos terminaram com código zero. A comparação confirmou conteúdo e metadados operacionais iguais. A comparação estrita de todas as datas não passou: houve 473 diferenças de mtime, exclusivamente nos 473 links simbólicos.

Não houve acesso ao roteador, upload, alteração de ambiente U-Boot, gravação, montagem de partições do aparelho ou reboot. O teste não executou qualquer binário ou script extraído do firmware.

## O que passou

| Verificação | Resultado |
| --- | --- |
| Arquivos regulares | 4.303; SHA-256 individual e tamanho iguais |
| Diretórios | 254; mesmos caminhos e metadados |
| Links simbólicos | 473; mesmos destinos, donos e permissões |
| Dispositivo de caractere | 1; mesmo tipo, major/minor e permissões |
| Arquivos ausentes ou adicionais | Zero |
| Permissões, UID/GID | Iguais em todas as entradas |
| Grupos de hardlinks de arquivos regulares | Iguais; nenhum em ambas as extrações |
| Datas dos arquivos regulares, diretórios e dispositivo | Iguais |
| Opções XZ | 12 bytes idênticos: 000004001c00090090004000 |
| Bloco / compressor / flags | 262.144 bytes / XZ / 0x6c0, iguais |
| Backup original | SHA-256 antes e depois igual |

A contagem interna de inodes do SquashFS permaneceu em 5.031. O inventário de caminhos tem 4.303 arquivos + 254 diretórios + 473 symlinks + 1 dispositivo.

## Limitação encontrada: datas dos symlinks

O unsquashfs 4.2 utilizado cria os links com symlink() e restaura seus donos com lchown(), mas não restaura suas datas. Isso foi verificado no código, unsquashfs.c, linhas 897–923, no scratch de compilação. Assim, cada extração recebe datas novas nos links e o remontador também lê essas datas novas.

Esse comportamento explica as 473 diferenças de mtime observadas. Não houve alteração no conteúdo dos arquivos nem nos destinos dos links. Não se afirma equivalência total de metadados: para preservação completa futura, a extração deve também restaurar os timestamps dos próprios symlinks sem seguir seus destinos.

O resultado bruto mantém status differences para não ocultar essa limitação. Nenhuma outra diferença foi detectada pelo comparador.

## Tamanho e integridade

- Imagem original: 39.870.464 bytes; bytes_used 39.589.954.
- Imagem remontada: 39.595.738 bytes, sem padding.
- Capacidade usada como referência histórica do volume: 39.870.464 byt
essa referência: 274.726 bytes, aproximadamente 268 KiB.
- Não se consultou a capacidade atual do volume no aparelho. A margem é pequena para futuras adições.
- SHA-256 original, antes e depois: 57d1427dad607e6f30373fff8c27681d6fc7d02c3276c0b3ef8aa45755f8e7d3.
- SHA-256 remontada: 26a1d6097c8727959539b05900c9730681bc91d7a95ad32fbcf70bc5034ffa9a.

A imagem inteira não é idêntica byte a byte ao backup. Layout, compressão e timestamps de construção podem variar. Foi comprovada a igualdade dos arquivos e dos metadados comparados, com a exceção explicitada.

## Arquivos e reprodução

- Ferramenta própria: ferramentas/testar_roundtrip_squashfs.py.
- Saída: artefatos/squashfs-roundtrip-20261002-211254/rootfs-rebuilt-offline.squashfs.
- Resultado detalhado: artefatos/squashfs-roundtrip-20261002-211254/resultado.json.
- Logs: 01-extract-original.log, 02-rebuild.log e 03-extract-rebuilt.log no mesmo diretório.
- Árvores de comparação, preservando links e dispositivo no filesystem Linux: /home/builder/t7-squashfs-roundtrip-20261002-211254/source e rebuilt. Não foram copiadas como diretórios para ExFAT.
- A ferramenta usa saída e scratch novos por execução, -noappend e não grava nos arquivos originais.

## Conclusão prática

A reconstrução offline do RootFS Acer com opções XZ correspondentes funciona. O erro anterior do unsquashfs padrão não impede esta reconstrução com a ferramenta compatível. O resultado não comprova montagem pelo kernel Acer, boot no Slot 2, suporte de um kernel ARM64 ou sucesso de uma release modificada.

Esta é uma remontagem do RootFS de fábrica, sem LuCI/pacotes ou mudanças de configuração adicionados. Não é um instalador nem uma imagem UBI/NAND completa. Um teste no aparelho continua separado e depende da identificação do volume real e do procedimento de recuperação. Avisar antes de qualquer teste no aparelho.
