# Boot temporário pela RAM — verificação estática do U-Boot Acer T7

Data: 02/10/2026.
Escopo: somente leitura dos originais; sem acesso ao roteador, servidor TFTP, upload HTTP, alteração de IP, compilação ou gravação. Este arquivo é o único documento novo desta etapa.

## Conclusão

O dump OEM contém os comandos tftpboot, bootm e source com entradas na tabela de comandos. O Failsafe tem uma ramificação que executa um script FIT antes de retornar para o reset. Portanto, existe um caminho tecnicamente sustentado pelo binário para HTTP → script em RAM → TFTP → bootm, sem persistir bootcmd.

Isso não é uma validação de boot no aparelho. Não demonstra que o kernel ARM64 inicia, que a rede do bootloader funciona na configuração atual, ou que uma imagem de diagnóstico está pronta.

O acionador existente não deve ser reutilizado sem revisão: ignora falha de TFTP e usa o mesmo endereço do upload HTTP, 0x44000000, incompatível com o planejamento anterior do initramfs.

## Evidências de comandos e ambiente

Os dumps Backups_MTD/backup_predator_t7_uboot_appsbl.bin e 2 - Backups Originais de Fabrica/appsbl.bin são idênticos: 1.572.864 bytes, SHA-256 3d6281190512ba50b83eea1a2d6fca69f01da5bb390d52b601e762ce8f1df2fc.

Tabela de comandos de 32 bits, com ponteiros de função Thumb:

| Comando | Offset da entrada no arquivo | Função |
| --- | --- | --- |
| tftpboot | 0x7bafc | 0x4a412499 |
| bootm | 0x7b480 | 0x4a409781 |
| source | 0x7bad4 | 0x4a40b071 |

Não foram encontrados os marcadores ncip, ncinport ou ncoutport terminados por NUL. Isso é consistente com Netconsole indisponível; não substitui configuração de compilação original ou teste dinâmico.

O backup de ambiente preservado informa:
- bootcmd=bootipq
- bootdelay=3
- ipaddr=192.168.10.1
- serverip=192.168.10.10
- stdin, stdout e stderr: serial@78AF000

Esses valores são de um backup, não leitura do estado atual. Ter valores TFTP no ambiente não significa que bootipq inicia uma transferência automaticamente. A UART do bootloader indicada no ambiente também não deve ser confundida com um endereço earlycon proposto para o kernel.

## A seleção do script depende de um marcador específico

A função em 0x4a446cd4 primeiro compara quatro bytes no offset 0x5c do upload com 0x73616c46, que em little endian corresponde a "Flas". Se coincidem, retorna tipo 2.

Depois verifica o cabeçalho inicial:
- UBI# → tipo 3;
- d00dfeed → tipo 0, caso a regra prioritária "Flas" não tenha coincidido.

Os dois acionar_tftp.itb examinados têm exatamente "Flas" em 0x5c. Sua descrição raiz é "Flash Iniciar TFTP". Não basta criar qualquer FIT com um nó script: é necessário preservar a seleção esperada pelo firmware OEM e verificar os bytes finais do arquivo.

Para a ramificação examinada de upload de firmware, em 0x4a44a576–0x4a44a588, o tipo 2 seleciona este formato literal:

```text
sf probe; imgaddr=0x%lx && source $imgaddr:script
```

O endereço usado é 0x44000000. O comando sf probe inicializa/detecta a flash; nessa sequência não há sf update, nand write ou saveenv. Os comandos contidos no próprio script continuam determinando seus efeitos.

Outras ramificações do mesmo manipulador contêm:
- sf probe && sf update ...
- nand erase ...; nand write ...

Consequência: não enviar o FIT do kernel diretamente ao Web Failsafe supondo que todo upload é temporário. A escolha incorreta de tipo pode seguir um caminho de atualização da flash.

## O reset vem depois da execução

Em 0x4a4483ce, o fluxo HTTP chama o manipulador 0x4a44a4b4. Depois:
- retorno negativo segue tratamento de erro;
- retorno não negativo passa por 0x4a44a434;
- em 0x4a4483e8 chama 0x4a402460, rotina identificada como do_reset na análise histórica.

O ramo source é executado dentro do manipulador, antes desse retorno. Se o script chama bootm e a transferência de controle ao sistema acontece sem retorno, o fluxo HTTP não alcança esse reset.

Se o script termina ou bootm retorna, o comportamento posterior depende do retorno do manipulador; há caminho para o reset. Um boot que trava também pode ser interrompido pelo watchdog.

Assim, o documento histórico recuperacao_e_boot_ram_acer_t7.md simplifica incorretamente a sequência quando afirma que HTTP necessariamente reseta antes que seja possível executar um sistema em RAM. O documento histórico foi preservado sem alterações.

## Acionador existente

Arquivos:
- 3 - Ferramentas de Recuperacao/acionar_tftp.itb
- Servidor_TFTP_Windows/acionar_tftp.itb

São idênticos: 33.582 bytes.
SHA-256: 2b2da1a9f5a9177ff82f8c85cef1f4f63dd9d389810ac46500459bac6dd0866c.

O nó /images/script contém:

```text
echo === ACIONANDO TFTP VIA LAN 1 ===
setenv ipaddr 192.168.1.1
setenv serverip 192.168.1.5
tftpboot 0x44000000 openwrt.itb
bootm 0x44000000
```

Achados:
1. Não contém saveenv: as duas alterações explícitas de IP são voláteis.
2. Usa 192.168.1.1/192.168.1.5, diferente dos IPs do backup e de parte dos guias. O script define seus próprios valores.
3. Executa bootm sem condicionar ao sucesso de tftpboot. Transferência falha não deve autorizar boot de dados anteriores ou incompletos.
4. O download reutiliza 0x44000000, endereço do acionador HTTP. A dependência do interpretador em relação ao script original durante essa sobrescrita não foi validada.
5. O initramfs auditado ocupa, quando descomprimido em 0x41000000, o intervalo [0x41000000, 0x44270000). Esse intervalo intersecta a origem em 0x44000000.
6. A descrição "LAN 1" é texto do artefato, não prova de porta operacional nem medição de link nesta etapa.

O script set_bootcmd.py usa fw_setenv para persistir bootcmd. Não serve ao objetivo de manter flash e ambiente persistente intactos; foi apenas lido, nunca executado.

## Procedimento proposto, ainda não executável

1. Definir um FIT de diagnóstico com initramfs mínimo, DTB e configuração coerentes, conforme a revisão de compilação anterior.
2. Definir o mapa completo da RAM: tamanho real, firmware seguro, bootloader relocacionado, buffers, acionador HTTP, FIT recebido, destino descomprimido, DTB e initramfs separado se houver.
3. Selecionar um endereço de recepção sem interseção com essas regiões. Nenhum novo endereço foi escolhido nesta revisão.
4. Especificar um acionador que mantenha a classificação tipo 2, nome de nó script compatível, tamanho aceito pelo HTTP e integridade verificável.
5. Exigir sucesso da transferência e validação do FIT antes de bootm. Condicional, comandos disponíveis de inspeção e parser OEM devem ser verificados antes de gerar o acionador.
6. Não incluir saveenv, fw_setenv, sf update, nand write, ubiupdatevol, comandos de instalação ou mudança de slot.
7. Fazer primeiro um ensaio controlado de recepção/validação, sem chamar bootm, quando houver autorização para teste no equipamento. Essa etapa interrompe o serviço temporariamente ao entrar no Failsafe.
8. Depois testar execução do initramfs. O objetivo inicial é comprovar uname -m, versão do kernel e shell do initramfs; resposta HTTP/Telnet isolada não basta.
9. Garantir que o initramfs não monte volumes persistentes com escrita nem execute scripts de instalação. Boot em RAM não elimina os efeitos que o sistema iniciado pode produzir.

O caminho sem UART permite iniciar o teste, mas não captura as mensagens de source/bootm nem o início da execução ARM64. O log do servidor TFTP comprova transferência, não boot. UART continua sendo o canal mais direto para localizar falha anterior à rede; ramoops exige driver inicializado e RAM persistente validada.

## Referências e limites

- [U-Boot source](https://docs.u-boot.org/en/latest/usage/cmd/source.html): executa scripts em memória e admite seleção de nó FIT.
- [U-Boot bootm](https://docs.u-boot.org/en/latest/usage/cmd/bootm.html): executa uma imagem FIT localizada em memória.
- A documentação atual explica a semântica geral; as particularidades OEM acima vieram da leitura direta do dump preservado.
- Nenhuma garantia de sucesso ou de recuperação física foi estabelecida.
- Scripts de análise existentes foram lidos; o código de auditoria executado apenas abriu arquivos locais e desassemblou bytes com ferramentas já instaladas.

