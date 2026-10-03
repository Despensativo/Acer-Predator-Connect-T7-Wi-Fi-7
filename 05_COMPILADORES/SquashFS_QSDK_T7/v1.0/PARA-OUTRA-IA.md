# Contexto para outra IA

Leia LEIA-PRIMEIRO.md, PROCEDIMENTO.md, manifesto.json e evidencias/resultado.json deste pacote antes de propor alterações.

Este é o “compilador oficial SquashFS T7” adotado como referência interna do projeto Acer Predator Connect T7/IPQ5332. A ferramenta não é oficial da Acer e não compila o kernel: são mksquashfs/unsquashfs 4.2 reconstruídos com patches públicos do OpenWrt e uma correção local de timestamps de symlinks.

Já foi comprovado offline: o backup de fábrica pode ser completamente extraído, remontado e extraído novamente com conteúdo e metadados comparados iguais, incluindo as datas dos 473 links. A imagem nova mede 39.595.654 bytes; as opções XZ de 12 bytes são idênticas ao original. O hash do backup original foi preservado. Logs, hashes e fontes estão disponíveis.

Não use o mksquashfs padrão do Ubuntu como substituto automático; confira o layout das opções XZ. Use a receita documentada, -noappend e saída nova. Preserve permissões, donos, symlinks e nós de dispositivo em filesystem Linux. Não remonte a árvore no ExFAT. As versões anteriores permanecem no projeto para rastreabilidade.

Não afirmar que o erro do unsquashfs padrão comprova “XZ proprietário para NAND 4K”. Não atribuir a falha de boot à TrustZone como fato: a última etapa executada no aparelho segue desconhecida. Este resultado não valida kernel ARM64, montagem OEM, boot do Slot 2 ou imagem de produção modificada. A imagem validada é do RootFS de fábrica remontado.

Continue preparando e verificando offline. Antes de qualquer teste no roteador, avise o usuário; este pacote não autoriza acessar, gravar, reiniciar ou mudar U-Boot. Identifique volume real e recuperação antes de propor teste no hardware. Diferencie fatos observados, inferências e itens ainda não comprovados.
