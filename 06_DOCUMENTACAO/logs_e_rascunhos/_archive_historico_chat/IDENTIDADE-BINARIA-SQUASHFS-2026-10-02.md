# Identidade binária versus equivalência de conteúdo — SquashFS T7

## Pedido e alcance

O usuário informou hashes MD5 dos volumes Slot 1 e Slot 2 e pediu conferir se a geração pelo compilador do projeto fica idêntica. Esta etapa comparou a imagem efetivamente gerada no teste completo com o backup local de fábrica. Não houve nova gravação, acesso ao roteador ou alteração dos arquivos comparados. O relato de clonagem do Slot 2 é informação fornecida pelo usuário; não foi verificado diretamente no aparelho.

## Correspondência com o original informado

| Arquivo | MD5 | Tamanho |
| --- | --- | --- |
| Backup local backup_predator_t7_ubi_rootfs.bin | 022605865983843c69395859b9ee7e64 | 39.870.464 bytes |
| RootFS remontado pelo compilador com mtime corrigido | d19a150765e7c7d6599f2aceb1a07299 | 39.595.654 bytes |

O MD5 do backup local coincide com o MD5 informado pelo usuário para os volumes clonados. Isso vincula a referência offline ao hash relatado, mas não substitui uma leitura atual dos volumes no aparelho.

A imagem gerada NÃO é idêntica byte a byte ao backup. Continua comprovada a equivalência de conteúdo e dos metadados comparados no round-trip: 4.303 arquivos, 254 diretórios, 473 symlinks e um dispositivo, sem diferenças. Os hashes SHA-256 atuais dos dois arquivos foram conferidos contra o resultado passed desse teste antes de registrar a conclusão.

## Diferenças observadas

- Primeiro byte diferente: offset 8, campo mkfs_time no superbloco. Original 1737086574, remontado 1790986858.
- Primeira diferença após o bloco de opções: offset 124. Portanto não é apenas data de construção ou padding.
- bytes_used: 39.589.954 no original e 39.595.654 no remontado, diferença 5.700 bytes.
- inode_table_start: 39.498.624 versus 39.494.456.
- directory_table_start: 39.534.110 versus 39.531.866.
- fragment_table_start: 39.585.006 versus 39.585.714.
- Mesmo compressor XZ, bloco 262.144 bytes, flags 0x6c0, 5.031 inodes e 214 fragmentos.
- Opções XZ iguais: 000004001c00090090004000.

Foi calculado em memória o hash da imagem gerada completada com 0x00 ou 0xff até o tamanho do original. Nenhum dos dois coincide com o original. Nenhuma imagem preenchida foi gravada como novo arquivo.

O backup inclui 280.510 bytes depois de bytes_used, majoritariamente 0xff, mas também zeros e outros valores. Essa cauda não é simplesmente padding uniforme. A função de eventuais marcadores não foi analisada nesta etapa e não se recomenda reproduzi-la cegamente. Também os hashes limitados ao payload SquashFS são diferentes, conforme o JSON de evidências.

## O que significa “idêntico”

- Clonagem dos bytes: copiar o original preserva o hash, desde que a comparação cubra o mesmo número de bytes e formato (volume lógico, não contêiner UBI ou NAND cru).
- Remontagem: exige preservar conteúdo, metadados e formato aceito. Não implica hash binário igual. Versão da liblzma, ordem interna de dados/inodes, timestamps e receita OEM podem alterar o resultado; não foi isolada a contribuição exata de cada fator.
- Modificação de RootFS, pacote ou configuração: necessariamente deixa de ser clone binário. Hash diferente isoladamente não demonstra corrupção ou rejeição pelo kernel.

Gerar exatamente o blob OEM exigiria reconstruir os detalhes do processo de construção original e sua cauda. A receita compatível do projeto não foi declarada equivalente ao toolchain original exato Acer. Não há garantia de reprodução bit a bit.

## Limites do diagnóstico relatado

Hashes diferentes entre Slot 1 e Slot 2 não comprovam por si só Kernel Panic. A mensagem xz: error reading stored compressor options observada no unsquashfs do PC descreve o leitor daquela ferramenta; não é automaticamente um log do kernel do roteador. A afirmação de cabeçalho XZ proprietário quebrado continua sem comprovação nesses termos: o layout Acer de 12 bytes foi reproduzido com patches públicos.

Clonar o RootFS elimina essa diferença de bytes para fins de teste controlado, mas ainda não comprova boot. Este comparador não testa kernel, bootargs, nomes/IDs/tipos dos volumes, seleção do slot ou overlay UBIFS. Rede, credenciais e Wi-Fi mencionados no relato não foram acessados ou extraídos nesta etapa.

## Artefatos

- ferramentas/comparar_identidade_binaria_squashfs.py: comparação somente leitura.
- evidencias/comparacao-binaria-squashfs-20261002.json: hashes completos/payload, campos do cabeçalho e diferenças.
- logs/comparacao-identidade-binaria-squashfs.json: saída preservada.
- Prova do conteúdo: artefatos/squashfs-roundtrip-mtime-20261002-212028/resultado.json.

A versão publicada COMPILADOR-OFICIAL-SQUASHFS-T7/v1.0 e seu ZIP permanecem intactos, com seus hashes e escopo original. Este relatório é um complemento de interpretação, sem prometer identidade binária OEM.
