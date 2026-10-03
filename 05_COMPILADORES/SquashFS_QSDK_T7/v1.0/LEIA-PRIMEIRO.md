# Compilador oficial SquashFS T7 — versão 1.0

Este é o conjunto de ferramentas adotado como referência oficial INTERNA deste projeto para remontar o RootFS SquashFS Acer Predator Connect T7. É uma reconstrução compatível validada offline, não uma ferramenta publicada, certificada ou homologada pela Acer. Também não compila o kernel Linux: empacota e extrai o sistema de arquivos.

## Estado validado

Em 2026-10-02 foi realizado o round-trip completo do backup de fábrica: extração, remontagem e nova extração. Conteúdo SHA-256 de 4.303 arquivos, metadados de 254 diretórios, 473 links e um dispositivo foram iguais; zero entradas ausentes, extras ou diferentes. As datas dos links passaram após a correção local. Opções XZ idênticas: 000004001c00090090004000. A imagem resultante mede 39.595.654 bytes.

Nada foi testado ou gravado no roteador. A montagem pelo kernel OEM e o boot não estão comprovados.

## Organização

- bin/: ferramentas x86-64 Linux/WSL prontas, não executáveis Windows ou ARM.
- fontes/: SquashFS 4.2 e quatro patches aplicados, incluindo a correção de datas de symlinks.
- scripts/compilar.py: compilação em scratch Linux novo, sem instalação global.
- scripts/testar_roundtrip.py: verificação completa parametrizada, offline.
- evidencias/: resultado passado, logs e prova da recompilação do pacote.
- documentacao/: relatórios completos e históricos.
- manifesto.json: commits, hashes, procedência e identidade da versão.
- SHA256SUMS: integridade dos arquivos do pacote.
- PROCEDIMENTO.md: dependências, comandos e critérios de sucesso.
- PARA-OUTRA-IA.md: texto pronto para compartilhar contexto.
- COPYING: licença GPL do SquashFS; as alterações locais acompanham o código/patch.

A imagem de firmware e as árvores extraídas não estão incluídas neste pacote. O caminho da imagem validada permanece no projeto original, registrado no resultado e no procedimento. As versões anteriores foram preservadas.
