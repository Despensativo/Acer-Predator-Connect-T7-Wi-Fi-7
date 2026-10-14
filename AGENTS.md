# Instruções de investigação e manutenção do Acer T7

## Entrada e documentação

- Leia primeiro o índice de `PLAYBOOK.md` e `TASK.md`, quando existir. Consulte a referência do assunto antes de executar comandos; não carregue o histórico inteiro por padrão.
- Use [docs/README.md](docs/README.md) para encontrar os documentos. Para contexto de IA, host versus roteador e validação, consulte [docs/IA-CONTEXTO.md](docs/IA-CONTEXTO.md).
- Preserve os READMEs, inventários e registros existentes. Registre estado da tarefa no checkpoint e lições duráveis na documentação pertinente, evitando repetições.

## Evidência e contexto

- Distinga estado observado, registro histórico, hipótese, candidato e resultado validado. Registre data/versão e referência da evidência.
- Faça buscas e extrações locais, com saída limitada. Leia intervalos e dependências relevantes; não injete dumps ou arquivos completos apenas por estarem disponíveis.
- Cada trecho relevante deve indicar origem, linhas ou offsets e versão/hash quando houver comparação de artefatos. Código descompilado não equivale a fonte original recompilável.

## Intervenções e validação

- Preserve acesso cabeado, original e recuperação antes de testes que possam interromper a rede. Altere uma variável relevante por rodada.
- Para uma gravação, confirme sistema ativo, alvo físico, cópia preservada, rollback e seletor final. Não deduza partição física apenas de `rootfs`, `rootfs_1` ou um exemplo antigo.
- Confirme inicialização, rádios, associação, tráfego e logs conforme a mudança. Retorno zero de `wifi reload` ou presença de um processo não comprova funcionamento.
- Compare desempenho com o mesmo cliente, associação/link e carga; não conclua ganho apenas de PHY rate, largura ou potência configurada.
