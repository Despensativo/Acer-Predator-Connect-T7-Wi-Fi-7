# Correção de datas de symlinks e novo teste completo — 2026-10-02

## Resultado

A correção foi feita em uma cópia isolada do unsquashfs 4.2. O teste completo de extração, remontagem e nova extração terminou com status passed: zero caminhos ausentes, adicionais ou com diferenças nos campos comparados, inclusive as datas dos 473 links simbólicos.

Nenhum acesso ou teste no roteador foi realizado. Nenhuma partição, variável U-Boot ou imagem original foi alterada. As ferramentas, imagens e resultados anteriores foram preservados.

## Correção

O extrator agora usa utimensat(AT_FDCWD, pathname, times, AT_SYMLINK_NOFOLLOW) após criar o link e restaurar seu dono. O timestamp é obtido do inode SquashFS (i->time), com resolução de segundos. A operação atua no próprio link, inclusive quando o destino não existe, sem seguir ou modificar o destino. Em caso de falha na restauração, o extrator encerra com erro.

O mksquashfs não foi modificado; seu hash permaneceu idêntico ao da versão anterior. A cópia corrigida foi compilada no scratch /home/builder/t7-squashfs-compat-20261002-v3. Binários anteriores não foram substituídos. Foram preservados o patch, as fontes compiladas e o log.

Patch: fontes/squashfs-preservar-symlink-mtime.patch.
Preparação: ferramentas/preparar_correcao_symlink_mtime.py.
Teste: ferramentas/testar_roundtrip_squashfs_mtime.py.
Log de compilação: logs/squashfs-symlink-mtime-compilacao.log.

## Verificações

| Item | Resultado |
| --- | --- |
| Arquivos regulares | 4.303, conteúdo por SHA-256 e tamanho iguais |
| Diretórios | 254, caminhos e metadados iguais |
| Symlinks | 473, destinos, donos, modos e mtime iguais |
| Dispositivo de caractere | 1, tipo, major/minor, modo, dono e mtime iguais |
| Caminhos ausentes/adicionais/modificados | 0 / 0 / 0 |
| Hardlinks de arquivos regulares | Grupos iguais, nenhum em ambas as extrações |
| Extração / remontagem / nova extração | Todas exit 0 |
| Opções XZ | Iguais, 000004001c00090090004000 |
| Bloco / compressor / flags | 262.144 bytes / XZ / 0x6c0, iguais |
| Hash do original antes/depois | Igual |

A comparação de mtime é em segundos, a resolução armazenada pelo SquashFS. Atime e ctime da extração não são usados para equivalência, pois não são timestamps originais preservados nesse formato. Xattrs não existem no backup usado e não estão habilitados nesta ferramenta. O teste não executa scripts ou binários extraídos.

## Imagem resultante

Diretório: artefatos/squashfs-roundtrip-mtime-20261002-212028/

- rootfs-rebuilt-offline.squashfs: 39.595.654 bytes.
- SHA-256: 460995361d98b91a92455257cc6d039fccb17816daecb52f6a5fa87fc437b925.
- Capacidade de referência histórica: 39.870.464 bytes.
- Margem: 274.810 bytes, aproximadamente 268 KiB. Capacidade atual do aparelho não foi consultada.
- resultado.json: status passed e evidências de comparação.
- Logs 01-extract-original.log, 02-rebuild.log, 03-extract-rebuilt.log.

SHA-256 do backup original antes/depois: 57d1427dad607e6f30373fff8c27681d6fc7d02c3276c0b3ef8aa45755f8e7d3.

Binários e fontes corrigidos: artefatos/squashfs-compat-mtime-20261002-v2/

- mksquashfs4-compat: 0b6341e0080f6f8f03ca6d06ce51e078da908f2b03d201f98035d33d86131ac6.
- unsquashfs4-compat-mtime: daa0fa607de1f454b064ce0b503985044ea58009b005daadbd127a8698a1f0a4.
- COPYING, fontes-compiladas.tar.gz e proveniencia.json.

## Alcance

O teste valida o round-trip offline do RootFS de fábrica nos campos descritos. A imagem completa não é idêntica byte a byte ao backup, pois a remontagem pode alterar a disposição dos dados e o timestamp de construção. Ela não inclui mudanças de LuCI/pacotes e não é um contêiner UBI/NAND ou instalador.

Montagem pelo kernel OEM, boot no Slot 2 e boot ARM64 continuam sem validação nesta etapa. Avisar antes de qualquer teste no aparelho.
