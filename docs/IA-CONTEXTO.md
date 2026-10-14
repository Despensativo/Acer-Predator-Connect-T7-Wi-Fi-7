# Contexto de trabalho para IA no Acer T7

Organização documental de 13/10/2026. Os procedimentos e resultados já registrados permanecem no `PLAYBOOK.md` e nas referências indicadas em [README.md](README.md). Este arquivo orienta sua consulta; não certifica o estado atual do roteador.

## Computador e dispositivo remoto

- Scripts com `uci`, `iw` e `ubus` pertencem ao roteador. Análises em Python podem rodar no computador, sobre arquivos locais ou dados coletados.
- Os registros do projeto descrevem BusyBox sem Python e Dropbear sem SFTP. Confirme o ambiente do alvo antes de depender desses detalhes. Nesse cenário, use ferramentas disponíveis no roteador, processamento local e `scp -O` ou transferência por pipe SSH quando apropriado.
- Em Telnet/shell interativo, aguarde o prompt esperado (`login:`, `Password:` ou prompt de shell) antes de enviar a próxima entrada. Não registre senhas na saída ou no checkpoint.
- O BusyBox registrado não aceita `sleep` fracionário. Quando esse comportamento se confirmar, use segundos inteiros ou `usleep` disponível; não presuma a presença desse comando.
- Antes de uma chamada `ubus`, inspecione os métodos disponíveis, por exemplo com `ubus -v list <namespace>`. Não adivinhe métodos ou argumentos.

## Como consultar o playbook

1. Leia o índice e as regras críticas.
2. Busque o subsistema, comando, arquivo ou sintoma.
3. Leia o bloco relevante e seus trechos dependentes, com limite de saída.
4. Confronte o registro com os artefatos e a versão atuais antes de uma alteração.

Uma linha muito longa também pode ocupar muito contexto. Limitar apenas o número de linhas não basta; limite caracteres/bytes devolvidos ao chat ou salve o resultado em disco e selecione seus trechos.

## Organização de fatos e estado

- `PLAYBOOK.md`: procedimentos e lições duráveis, com evidência e escopo.
- `TASK.md`: objetivo atual, alterações feitas, resultados, pendências e próximo passo.
- Documentos de relato/feedback: preservar sua natureza histórica e a cronologia.
- Inventário de arquivos: caminho, origem e status da alteração; validar que corresponde ao artefato candidato atual.

Não duplique todo o playbook em um resumo. Escolha o pacote de contexto da tarefa e preserve ligações para os originais. Se uma hipótese precisar de mais código ou logs, extraia o material necessário em vez de completar lacunas por suposição.

## Critérios de intervenção

Configuração, scripts, módulo de kernel e firmware são camadas diferentes. Valide o tipo de alteração e a compatibilidade correspondente. Uma compilação bem-sucedida ou correspondência isolada de vermagic não demonstra funcionamento no rádio.

Mapas de NAND/UBI e resultados antigos são referências. Para uma gravação, mapear novamente sistema ativo e alvo físico, preservando recuperação. Após alterações que exigem reinicialização, confirmar novo boot e comportamento dos rádios/clientes sob a carga relevante.
