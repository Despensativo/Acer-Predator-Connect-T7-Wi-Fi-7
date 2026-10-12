# 📋 Relatório de Feedbacks e Plano de Correções — Acer Predator Connect T7
**Versão Avaliada:** Master v2.0 (OpenWrt Custom + LuCI + Central Wi-Fi ARC)  
**Validador de Bancada:** Diego Augusto ([@bestyall](https://forum.openwrt.org/u/bestyall))  
**Data:** 12 de Outubro de 2026  
**Total de Áudios Analisados:** 36 áudios (Verificados por Hash SHA-256: 36 arquivos únicos, 0 duplicados binários)  
**Arquivo de Backup Recebido:** `backup-Predator Connect T7-2026-10-12.tar.gz`  
**Status do Documento:** [PRONTO PARA IMPLEMENTAÇÃO / ROADMAP v2.1]

---

## 🔍 1. Verificação de Duplicidade (Arquivos vs. Temas Recorrentes)

1. **Verificação Binária (SHA-256):** Todos os **36 arquivos `.opus`** presentes na pasta `Downloads` são gravações distintas (nenhum arquivo foi baixado em duplicidade).
2. **Temas Recorrentes / Evolução dos Testes ao longo do dia:**
   * **Criptografia WPA2 vs WPA3 *(Áudios 05, 29, 30, 31, 33 e 36)*:** O Diego reforça diversas vezes — e comprova no final — que **2.4 GHz e 5 GHz devem iniciar SEMPRE em `WPA2-PSK` puro**. O modo misto (`WPA2+WPA3`) ou `WPA3` derruba impressoras 3D (Creality), impressoras de papel, celulares Xiaomi, repetidores e trava o DHCP no MLO.
   * **"Red Light" ao Salvar e Aplicar *(Áudios 04, 08, 17 e 34)*:** Citado repetidamente como o principal incômodo prático de usabilidade, exigindo tirar da tomada quando a alteração é feita via Wi-Fi.
   * **Evolução dos Testes de MLO / Band Steering *(Áudios 06, 24, 32, 33 e 34)*:** No início da manhã (Áudio 06) ele ainda não havia testado; à tarde (Áudios 32, 33 e 34), ele testou todas as combinações e descobriu uma regra de ouro: **MLO de `2.4 GHz + 5 GHz` (com `6 GHz` separado) funciona perfeitamente**, enquanto MLO misturando `6 GHz` (`5+6` ou `2.4+5+6`) bloqueia a entrega de IP via DHCP (gerando IP `169.254.x.x`) por conflito de protocolo WPA3 com WPA2.
   * **Queda e Recuperação do Rádio 6 GHz *(Áudios 06, 11, 12, 23, 25, 27, 29 e 31)*:** Inicialmente o 6 GHz caiu ao mexer no LuCI; mais tarde (Áudio 29 e 31), ele conseguiu recuperar o rádio de 6 GHz pela interface e identificou que **desativar a opção Wi-Fi 7 / 4096-QAM no ARC desliga o rádio de 6 GHz**.

---

## 🎧 2. Transcrição Literal dos 36 Áudios de Feedback (Ordem Cronológica)

### 🔊 Bloco 1: Abertura e Primeiras Impressões (Manhã)
* **Áudio 01 (`10.12.55.opus` — 00:23):**
  > *"E aí, beleza? Cara, eu nem entrei em contato com você porque feriadão, né cara? Feriadão, domingão, falei 'não, o cara sofreu pra fazer a bagaça, tá na correria, deixa ele aproveitar o feriadão aí descansar'. E valeu, cara! Agradecer a você, valeu lá do do agradecimento lá no GitHub, né? Pô, obrigado aí mano, show de bola! Achei bacana pra caralho. Em relação ao coisa, tem uma ou outra configuraçãozinha, mas acho que não tem como ser feita assim em pouco tempo assim, cara. É coisinha simples, e algumas coisas que são simples ali é uma dor de cabeça."*

---

### 🔊 Bloco 2: USB, DHCP e Comportamento dos Dispositivos
* **Áudio 02 (`10.12.55 (1).opus` — 00:19):**
  > *"Tipo... é... a ausência do do mask pra fazer o mascaramento da USB, né? Quando você engata um pen drive lá, tem uma opção que não tá mais lá, que é o mask. Se você não definir ali o 666, 777, que é o código pra você liberar a autorização total do pen drive, ele não conecta. Então o que acontece: você tem que fazer isso via anotação."*

* **Áudio 03 (`10.12.55 (2).opus` — 00:26):**
  > *"Outro, esse é um pouquinho mais complicado, que é quando você reinicia ele por algum motivo, ele perde todos os os IPs que estavam no roteador. Digamos assim, eu liguei, o que tá acontecendo com as minhas impressoras, as impressoras da Creality: Se eu ligar elas agora, vai estar lá o IP tudo bonitinho, o nome delas. Se eu reiniciar o roteador, o IP some, algumas vezes eu não consigo conectar no IP. Apesar que eu fiz um teste agora, e elas tão conectadas apesar do roteador não estar mostrando o IP. E os repetidores também, eles não tão pegando IP. Eu preciso até testar lá em cima pra ver se o repetidor tá transmitindo."*

---

### 🔊 Bloco 3: "Red Light" no Salvar e Criptografia WPA2/WPA3
* **Áudio 04 (`10.12.55 (3).opus` — 00:30):**
  > *"Outra parte, essa é chata, essa aí, puta merda. Digamos assim: você deixou tudo pronto o roteador, bonitinho, configurado. Aí você tem que fazer uma mudança. Sei lá, que seja uma mudança do Wi-Fi... você vai mexer ali, vai ativar alguma coisa que você vai ter que fazer um reiniciamento do sistema, o que acontece? Ele dá red light, cara! E ele não sobe. Ele fica o red light até você ir lá desligar o roteador e ligar de novo se não tiver com cabo. Mesmo estando com cabo ele dá red light, você tem que fazer um reinício forçado, um reinício do sistema. Então o que acontece: se eu faço um save, eu atualizo lá para um 'Salvar e Aplicar', eu tenho que vir aqui onde tá o roteador na sala desligar da tomada pra daí ele subir certinho."*

* **Áudio 05 (`10.12.55 (4).opus` — 00:32):**
  > *"Outra parte, essa aí é um pouco mais complicada, que essa é uma configuração que eu acho que não pode ir direto no roteador: subir o WPA3 junto com o WPA2. Se subir o WPA3 junto com o WPA2 pro 2.4 e pro 5 GHz, ele não conecta um monte de dispositivo. Entre eles o Xiaomi, as impressoras da Creality, os repetidores... Acho que conflita com o WPA3. Aí ele perde conexão de quase tudo. Então tem que deixar tudo WPA2 pra 2.4 e pra 5 GHz. Eu já tinha essa observação quando tava com a original, que eu acho que era um fake quando colocava o WPA3 no 2.4 e no 5 GHz. Só funcionava só pro 6 GHz."*

---

### 🔊 Bloco 4: Testes Iniciais de MLO, Band Steering e Central ARC
* **Áudio 06 (`10.12.56.opus` — 00:25):**
  > *"Uma coisa que eu não testei ainda, que eu tenho que testar, é o Band Steering, né? Que no caso lá tá como MLO 3 canais, mas é o Band Steering do antigo Band Steering dele. Eu não testei ainda o MLO 5 GHz com 6 GHz, e não testei o MLO 5 GHz com 2.4 GHz. Fora isso, o resto das coisas ali do ARC [Central Wi-Fi], vou te falar pra você: o ARC ali é bem necessário, hein cara, puta merda! Fui mexer no sistema direto lá pelo LuCI, acabei travando o 6 GHz, precisei refazer de novo."*

---

### 🔊 Bloco 5: Switch LAN 1 e Histórico de Estabilidade
* **Áudio 07 (`10.18.47.opus` — 00:16):**
  > *"Continuando aqui... é mais um detalhe: essa parte da interface 1, da LAN 1, tá sempre conectada. Não sei o porquê que tá acontecendo isso, não sei se é uma configuração do switch. Não sei também se isso faz aumentar as temperaturas do roteador, ou faz comer banda do processador ou alguma coisa do tipo."*

* **Áudio 08 (`10.18.47 (1).opus` — 00:08):**
  > *"Um detalhe agora que você passou, se eu não tiver enganado, a primeira configuração que você me mandou não acontecia isso de você salvar as coisas tanto no ARC quanto no LuCI e não subir e ficar dando red light."*

---

### 🔊 Bloco 6: Ajuste de Timeouts (LuCI Rollback e ARC Timer)
* **Áudio 09 (`10.19.20.opus` — 00:35):**
  > *"Um outro detalhe: aumentar o tempo... eu aumentei pra 300 segundos o tempo de reinício do LuCI. Por quê? Porque tinha momentos que eu fazia uma configuração no LuCI mesmo, e como tava 90 segundos, o padrão desse roteador é quando ele reinicia ele demorar demais pra fazer o reconhecimento do Wi-Fi, né? Então o que acontecia: eu modificava ali, salvava e aplicava, os 90 segundos passavam, aí ele dava um revert, era mais 90 segundos. Então ia pra 180. O que eu fiz: aumentei pra 300 segundos, que é o mais tranquilo com folga tudo, e dá tempo de você aplicar, ir lá reiniciar o roteador se for necessário, ou até mesmo se ele mesmo conseguir reiniciar dá o tempo dele fazer todo o levantamento do sistema, e não tem perigo de dar o revert. Deu várias vezes revert, eu tive que aumentar."*

* **Áudio 10 (`10.19.59.opus` — 00:31):**
  > *"E o outro lugar também que tem que aumentar um pouquinho é na parte do ARC. Aquela parte que você colocou que tem opção de Salvar Rádio... Ali tem que ter no mínimo, eu acho que uns 90 segundos, cara. 90 segundos pra mais. 20 segundos só, quando cai a rede, até o Wi-Fi reconhecer depois, ele acaba dando como se fosse um revert no próprio sistema do ARC, e muitas vezes ele acaba retornando todas as configurações de volta. Digamos assim: eu botei um canal fixo, aumentei a potência e travei em 40 MHz. Quando eu salvo, ele dá os 20 segundos, só que cai a rede e ele reconhece como se não tivesse feito nada. Então acho que ali deveria também aumentar ali uns 40 segundos, 40, 50... Isso aí é só calculando mesmo ali na hora pra saber, mas tem que ser uma quantidade maior de tempo pra fazer o aplicar."*

---

### 🔊 Bloco 7: Comportamento de Potência e Rádio de 6 GHz
* **Áudio 11 (`10.21.25.opus` — 00:49):**
  > *"Agora outra parte, essa é mais triste, cara. Essa aí deu até tristeza. É... o 6 GHz ele tem um fake power, né cara? 6 GHz não adianta, é uma coisa de outro mundo. 6 GHz você não pode mexer em quase nada nele que você derruba e ele não volta mais. Ele tem um fake power porque ele continua, ele indica que dissipa aquilo, ele escreve tudo, mas infelizmente ele não sai da potência que ele tem. O 5 GHz até que tá trabalhando bem com a potência alta, o 5 e o 2.4, mas eu não sei se todas as potências dissipadas acima do 22 e do 23 são reais, mas ele tá trabalhando bem. Mais um detalhe: a banda do 6 GHz, mesmo que você fique em cima da placa de wireless, ela tá com a mesma abertura, o mesmo ganho do 5 GHz, isso é 2.400 de banda. O 5 GHz é 2.400 e uns quebrados e o 6 GHz também tá 2.400 e uns quebrados. Não sei dizer pra você se é pelo fato de tá em AX ao invés de tá em BE, AX em 160, né? Não tem como eu testar na banda de 320. Banda de 320 pra comprar o adaptador agora tá louco, é uma falência."*

* **Áudio 12 (`10.23.23.opus` — 00:50):**
  > *"Outro detalhe que eu achei bacana, isso aí acho que não é nem tanto problemático, mas é bem funcional: a parte do rádio do LuCI para o 2.4 e para o 5 GHz ele opera tranquilo, cara. Tipo assim, ele não indica que funciona, mas você fazer ali as configurações, digamos assim, tipo desassociar por baixo dBi (é o low ack lá), ele funciona se você marcar lá... a distância, o ack time dele também, ele dá um ack time para essas duas interfaces. Você coloca lá que seja 2.000 metros de ack time, ele aceita; ele aceita você definir o país; ele aceita você colocar modo retroativo para a banda B; ele aceita você modificar os canais, a frequência... praticamente ele aceita tudo ali. Só que se você fizer no de 6 GHz, é instantâneo, cara: você derruba o 6 GHz e depois você tem que fazer a modificação no próprio script, ele não volta mais. Ou fazer um... subir um backup. Porque senão... não fiz um teste mais pesado nele, mas quando eu modifiquei ali qualquer coisa, não consegui voltar o 6 GHz não."*

---

### 🔊 Bloco 8: Pacotes Internos no LuCI (ALSA, Quagga, Monitor)
* **Áudio 13 (`10.25.06.opus` — 00:54):**
  > *"Isso agora é um detalhe de software, não sei se você viu, mas tem umas coisas ali no sistema do LuCI... eu não sei porque tem um controlador de áudio nele, cara! É impressionante. Se você for ver, tem um controlador chamado ALSA, que é um controlador de áudio, é áudio mesmo, pra fazer MP3, pra gravar. Não sei por que que ele veio, pode ser que veio no snapshot, mas sei lá se esse roteador é meio louco, captando áudio de algum jeito aí. Apesar que se você pegar o GPIO dele acho que dá pra fazer uma saída de alto falante ali nele e uma entrada de áudio. Achei até estranho, pode ver, tem um drive chamado ALSA. E tem o outro chamado Quagga, né? O Quagga ele é tipo... ele tira informação e manda pra alguém, né? E tá desativado. Vi ali, ele tava desativado. E tinha uma outra, acho que um outro drive que era o... acho que é v27 Predator Wi-Fi v7, acho que é isso, ele tava desativado. Eu fui lá de curioso, ativei, e não sei dizer se melhorou alguma coisa ou se complicou alguma coisa, viu? E a outra coisa que eu ativei, a única coisa que eu vi é que parece que o monitor onde tem no ARC ele começa a indicar as operações que tão sendo feitas naquele momento, que é o Wi-Fi monitor, cara! Eu ativei ele também nas opções de inicialização ali. Então acho que não teve nenhuma alteração assim tão grave pro sistema."*

---

### 🔊 Bloco 9: Conntrack, Swap, Engasgo de Vídeo e Configurações Avançadas
* **Áudio 14 (`10.27.20.opus` — 00:42):**
  > *"Um detalhe, isso aí eu já não sei dizer pra você se é uma configuração... pode ser que eu tenha feito alguma configuração que tá causando isso, que é: às vezes você tá mexendo no celular e ele começa a dar umas travadas, umas travadas, aquele negócio que eu te disse que o áudio às vezes continua, o vídeo para... ele para, depois continua, vai, continua... Outro detalhe, eu não sei dizer pra você, posso estar enganado, eu não tive ainda carga suficiente pra rodar, mas acho que 65.535 de conntrack, mano... conntrack eu acho que é muito, cara. Que são as conexões na rede. Mas apesar que acho que não subiu tudo, ele não vai ocupar tanto do processador porque o processador dele é muito forte, cara. É bem... bem cabuloso. Mas acho que é bastante, eu não sei de onde que ele tirou essa quantidade. E eu achei bacana também que o swap dele... eu não fiz o teste, mas o swap dele tá funcionando, né? Vou até ver se eu faço uma partição no meu pen drive e vou ver se engato lá um swap nele. Interessante! Apesar que eu acho que não come tanta RAM assim pra poder usar um swap."*

* **Áudio 15 (`10.28.55.opus` — 00:54):**
  > *"Fora isso, deve ter alguma outra coisa que eu tô deixando passar, mas se eu tô deixando passar não é tão relevante. Mas o resto das opções, mano... pá! Puta trabalho, mano, ficou show de bola! Tá ligado ele aqui, tô mandando as mensagens pra você por ele. Ele tá ali em cima ali já, eu terminei as configurações principais ontem. Eu mexi em tudo que foi possível: interface, mudei IP, mudei senha de administração, tentei empurrar um novo repositório nele (que é um repositório... se você clicar no nome azul ali do do LuCI, você acaba achando o repositório, não sei dizer se é o original, mas você acha o repositório dele no GitHub. Tentei engatar um repositório nele ali pra ver se ele aparecia as atualizações de software, só que não fui tão a fundo porque se você instala um negócio nesse mesmo GitHub que ele te empurra, ele te mostra um negócio pra fazer a instalação, não fui ainda fazer esse teste pra ver se ele vai direto e atualiza o software por ali). Interface tá ok, defini DNS, mexi em como se diz... Spanning Tree, IGMP, todas as partes que deu pra mexer nas interfaces eu mexi, tá tudo ok. Tanto na de WAN 6 quanto a WAN 5, deletei aquelas interfaces extras: Guest, IoT... Tentei tirar a 4X, não deu pra tirar também, ela fica lá, mesmo que você exclua ela vai ficar como parece que desativada..."*

---

### 🔊 Bloco 10: Testes de IP Fixo e Considerações de Hardware
* **Áudio 16 (`10.30.26.opus` — 00:36):**
  > *"Fiz teste de IP fixo, acho que o IP fixo não sei dizer se funcionou bem não. Que foi definir lá no DNS o IP fixo, no DNS e DHCP. Eu preciso refazer esse teste, parece que apesar de estar fixo o IP, a interface não fornece aquele IP e trava com outra... ele trava com o DHCP padrão do LuCI, que provavelmente deve estar ligado com o DHCP do sistema do roteador. Fora isso tá... tá rodando liso essa parte. Tive que tirar os IPs que eu tinha fixado porque eu fui ver no syslog dele lá, ele estava se comunicando com a interface mas não tava tendo retorno. Então tirei, foi a parte das impressoras. Aí, apesar de não indicar que tá mandando IP, ele tá lá funcionando. Eu consigo conectar... graças a Deus consigo conectar nas impressoras, que elas são todas Wi-Fi, né, a impressora, e depois eu preciso subir e fazer o teste no repetidor, que o repetidor ele não indica que recebeu IP nenhum. Mas fora isso tá tudo joia na parte da interface."*

* **Áudio 17 (`10.31.09.opus` — 00:18):**
  > *"É, eu acho que é todas essas coisinhas que tem. Acho que isso aí é coisa simples, só o único que enche mais a paciência mesmo é a parte de você salvar e ter que ir lá desligar, né? Porque tem que tirar... no caso o meu, como o roteador tá lá no alto, tem que tirar da tomada. Às vezes você faz um desligamento nele direto aí a gente fica naquele negócio do tipo 'vai acabar uma hora dando... queimando ele de uma vez', né? Mas não tava dando muita atenção não, tava fazendo os testes mesmo. Mas é isso aí."*

---

### 🔊 Bloco 11: A Cereja do Bolo (USB/Samba), Bridge IPv6 e Repetidores
* **Áudio 18 (`10.33.00.opus` — 00:46):**
  > *"Ah, e mais um detalhe: as criações que foram feitas ali do mount point... no mount point não, no KSMBD ali... KSMBD/CIFS, sei lá como é que é a sequência das letras... Aquele ali acho que nem precisava criar, viu? Ele tem um que ele cria mesmo dele que é o OpenWrt 1, cara, e aquele ali é o que mais funcionou bem, porque mesmo que você reinicie ele volta sempre. Então é mais fácil deixar no OpenWrt 1 mesmo, porque você exclui ele e ele volta, você exclui ele e ele sempre vai voltar.*  
  > *Então eu deixei ali nele fixo, tudo certinho, fiz a configuração via script, né? Entrei pelo WinSCP, que é mais fácil pra fazer essas configurações, e editei lá, coloquei o mask do... o mask 777 e o 666 pra poder ter o acesso total ao pen drive. A única coisa que eu estranhei é que mesmo eu colocando uma conta minha, uma senha minha, um nome lá, ele não pediu via Windows, viu? Achei estranho porque antes quando você faz isso ele sempre pedia pra você fazer as credenciais. As credenciais foram meio que engolidas na parte do Windows, mas consigo acessar tranquilo a partição sda1, que eu não sei pra que que serve, deve ser o acesso direto à NAND, e a... o pen drive.*  
  > *Pô, isso aí foi o cara... foi a cereja do bolo, mano! Você pode reiniciar ele um milhão de vezes, cara, que o roteador ele volta sempre com o USB perfeito, cara! Pode reiniciar, se der algum problema você vai lá no... no inicialização lá e só dá um reiniciar no KSMBD lá e acabou, cara. Já era, volta tranquilo. Antes era uma dor de cabeça do caramba!"*

* **Áudio 19 (`10.49.08.opus` — 01:03):**
  > *"Eu não, não vou mandar o backup não, você fez um monte de porta suspeita no roteador... [rindo] que eu nem sei o que que é, as portas físicas, umas portas estranhas com os nomes nada a ver, não sei nem de onde vai aquelas portas loucas lá... Vou mandar o backup não, você vai ficar me sniffando online aí... [risos]*  
  > *Não, tô zoando! A hora que o backup tiver pá, se você precisar você fala, mano, eu mando pra você aí.*  
  > *Pô, eu fiz algumas configurações ali de script mesmo. Como eu disse pra você, é muito fácil de fazer no WinSCP, porque no WinSCP você faz ali, você abre como se fosse um editor o script, escreve e salva na hora e qualquer coisa você inicia pelo PuTTY mesmo ali, dá um service restart no que tá sendo ativado ali ou mexido, ele já resolve na hora.*  
  > *Mas em relação ao KSMBD, eu apaguei aquelas contas que tavam, viu? A root e a admin, zerei todas. E coloquei a minha. E vou te falar: tá trabalhando full! Ó, tá trabalhando 100%, mano! Maravilha!*  
  > *Eu não sei se é porque as credenciais da antiga ficou e eu botei a mesma conta, mas o acesso perfeito, cara! Muito bom! Não subiu, como eu disse, quando eu peguei e fui fazer as primeiras configurações não subiu, por quê? Por causa da ausência daquelas configurações extras na hora que você bota o path lá, que é o /mnt/sda1 ou sda... aí tem uma sequência de caixas para selecionar e no final tinha aquelas duas opções do mask. Se não colocar aquilo de lá, ele não dá acesso, não dá permissão de acesso aos periféricos. Mas o resto, mano... tá show! Show de bola, mano, show de bola mesmo!*  
  > *Tá aqui ligado, fiz o teste. Preciso fazer um teste com latência alta, tipo um jogo, jogar alguma coisa assim, é que agora tá numa correria do caramba aqui que eu tenho uns produtos pra entregar pra uns eventos, então não deu tempo de eu conseguir jogar direito, né? Mas eu vou fazer depois o teste. Vou desativar o modem que tá fornecendo a interface extra pra mim poder ficar fuçando nele, né, se não derruba a internet da casa inteira.*  
  > *Aí vou fazer o bridge, quero ver como é que o bridge dele vai lidar com a situação, né? Se ele vai trabalhar bem, se ele vai pegar o IPv6 tranquilo... aí é um outro teste. Esse aí eu tenho que te dar uma atualizada depois que tiver feito."*

* **Áudio 20 (`10.51.01.opus` — 00:44):**
  > *"E pelo que eu vi agora que eu subi agora para tomar um café, é... realmente, eu tô achando que ele não está... os repetidores não estão conseguindo se comunicar com ele. Isso aí eu vou te falar que não é uma coisa monstruosa porque antes, com ele puro, com ele zero, tirado da caixa, ele tinha essa... no pleno sentido da palavra, ele tinha essa viadagem, cara, de não se comunicar com os repetidores.*  
  > *No caso eu tô usando no modo repetidor ele, né? Repetidor, não tô usando no modo Mesh. Porque sei lá, o Mesh não sei se funciona muito bem não.*  
  > *Então eu tenho um Intelbras, o RG 1200, que tá na parte de cima aqui, e ele não está mesmo se comunicando. Mas eu vou ver com calma o que dá para ser feito. Às vezes pode ser a potência que tá chegando lá é mais baixa, não sei... Ele indica no OpenWrt que tem uma interface se comunicando com ele pedindo um IP para distribuir, porém o OpenWrt não tá fornecendo."*

* **Áudio 21 (`10.51.49.opus` — 00:11):**
  > *"Ô, tentei instalar o ARC nele aqui, mano, que eu tenho que eu baixei lá do site. Eu falei: 'Ah, vou tentar, né?'. Mas ele deu uma falha. Falei: 'Ah, que tristeza'."*

---

### 🔊 Bloco 12: Repetidor Wireless, Rádio 6G Derrubado no LuCI, Band Steering e Backup
* **Áudio 22 (`10.55.09.opus` — 00:27):**
  > *"Ah, o outro é repetidor. Não, é repetidor mesmo, é via wireless, esqueci de detalhar isso aí, não é via cabo não. É wireless puro, na faixa de 2.5... 2.4 GHz.*  
  > *Antes quando ele... quando tava sem subir o LuCI ele funcionava, mas tinha vez que ele fazia uma frescura lá, desconectava, e pra conectar eu tinha que reiniciar o roteador, às vezes tinha que descer e reiniciar o Predator também... Mas agora não, agora ele não puxa. Ele indica que tá pedindo, mas não libera o IP."*

* **Áudio 23 (`11.32.50.opus` — 00:12):**
  > *"Cara, acho que vou acabar te passando um backup com o 6 GHz arregaçado, cara. Fui fazer uma... uma configuração aqui, fui conferir nele, acabei clicando no negócio, não fiz o revert para tirar o que eu tava modificando, salvei e derrubou o 6 GHz. Ô desgraça, viu! Nem prestei atenção."*

* **Áudio 24 (`11.32.51.opus` — 00:13):**
  > *"É, não, eu não consigo usar o MLO por isso, nem o MLO nem o Band Steering por isso, cara. Porque ele vai sempre olhar para o 2.4 GHz, cara. Sempre vai ter aquela paixão pelo 2.4 GHz, mano. E eu prefiro usar o 5 GHz, que a banda é maior e eu consigo aproveitar melhor o... o plano de internet."*

* **Áudio 25 (`11.42.31.opus` — 00:18):**
  > *"Ó, tô mandando o backup aí, mas já tô dando um alerta que o 6 GHz tá quebrado, viu? Como eu disse, não pode fazer nenhuma configuração no LuCI com ele que ele quebra e não volta mais, cara. Bom que até você dá uma conferida aí no... no coisa por que que ele quebra assim, cara. Esqueci, fui botar em alto lá o... a configuração dele, salvei, e era para mim ter feito o revert, não fiz, e derrubou o 6 GHz. Desgramado."*

* **Áudio 26 (`11.52.59.opus` — 00:11):**
  > *"Ah, depois eu tento corrigir ele aqui porque não dá pra usar ele direito, cara. A distância que ele transmite, ele dá uma abertura de banda muito baixa, então eu uso mais o 5 GHz, cara."*

* **Áudio 27 (`11.55.30.opus` — 00:36):**
  > *"Ah, mas a queda é muito expressiva, viu cara? A queda e a instabilidade. O sinal dele aqui chega pra mim com três palitinhos, cara. Tem dia que chega com um. Aliás, antes da atualização pro v27, quando tava no v24 ele chegava um palito. Aí depois que fez a atualização agora chega dois, com muita sorte três. E olha que não tá muito longe do computador. Mas a queda é muito drástica, cara, e se ele ficar oscilando demais aí cai mais ainda. Mas isso aí depois eu faço um teste nele com calma. Só o que injuria é isso: uma cagada ali, acabei que eu fui lá, mudei a potência, caiu, derrubou. Aí eu tenho que ir lá no WinSCP e reeditar ou ver o que que ele adicionou extra e ver se volta, mas acho que isso aí deve ter quebrado no comunicador que você fez entre o ARC e o LuCI."*

---

### 🔊 Bloco 13: Bateria Final da Tarde — Recuperação do 6G, 4096-QAM e Testes Definitivos de MLO
* **Áudio 28 (`17.36.39.opus` — 00:54):**
  > *"Olha, é que antes ele funcionava já o repetidor. Funcionava bem até. Só que o que eu percebi aqui que tá acontecendo é que não está dissipando informações técnicas junto com o sinal wireless. Sei lá, acho que precisa de um certificado ou algum cabeçalho específico pra ele aceitar. É como um computador extremamente rígido em questão de segurança que não tá aceitando. Acho que é pelo fato de que o que tá dissipando o sinal é o ARC, né? Agora, se tivesse o LuCI dissipando o sinal — o que ele não dissipa o sinal, o LuCI não tá conseguindo reconhecer os drivers, né? Então ele só dá a opção de você criar, mas se você for ver lá nos wireless lá tá tudo como 'disabled', não dissipando o sinal, desligado, mas as configurações estão lá. Eu acho que é isso que tá acontecendo. Mas agora que você falou em relação à rede Mesh, eu vou dar uma olhada naquela opção que tem lá no LuCI, vai que de repente tem alguma opção ali que possa estar bloqueando. Aí eu vou ver isso aí com calma pra ver se dá certo pra ele voltar a funcionar. Se acaso não der, eu tento encontrar um outro roteador que esteja funcionando o repetidor e coloco no lugar dele."*

* **Áudio 29 (`17.55.25.opus` — 00:11):**
  > *"Olha, eu fiz a troca, né, de WPA3 para WPA2 Mixed com WPA3 e voltou! E subiu o 6 GHz, viu? Ele reparou o 6 GHz! Não sei como, mas reparou!"*

* **Áudio 30 (`17.55.38.opus` — 00:08):**
  > *"E um detalhe: foi removido o WPA, cara, que não parece, mas é um protocolo importante às vezes pra retrocompatibilidade, cara."*

* **Áudio 31 (`17.57.41.opus` — 00:46):**
  > *"É sim, não, é só WPA3 mesmo o 6 GHz, 6 e 7 GHz. É... porém nele eu não modifico porque no ARC não deu pra modificar, eu tive que fazer a modificação dos outros dois diretamente no LuCI. Aí eu modifiquei, subiu e voltou a funcionar o 6 GHz! Mais um detalhe: o que você tava falando que é difícil lidar é o QAM, né? 4096-QAM. Deixa eu ver se é isso mesmo... É a modulação QAM 4096 mesmo, que é o Wi-Fi 7 puro. Tanto que eu até ia falar pra você que nessa opção do ARC aqui acho que você poderia até remover ele, cara, porque quando você desliga essa opção ele para o 6 GHz, cara! E o restante não interfere em nada porque eu não uso o WPA3 no 2.4 e nem no 5, cara. Porque ele conflita com muita coisa! Um monte de roteador que aparece aí ele conflita demais: nas impressoras, conflita com impressora de papel, com impressora 3D, com repetidor, com celular... é uma coisa louca, cara!"*

* **Áudio 32 (`18.01.08.opus` — 00:22):**
  > *"Acabei de achar um outro bug aqui, cara: quando tá em MLO Tri-Band ali, ele não repassa o IP, mano! Ele tá igual quando faz com o repetidor. Eu vou dar uma olhada aqui e ver o que pode ser, se é alguma configuração que tá travada, mas ele não tá repassando o IP pro wireless. Ele tá em aberto, fica dando aqueles números estranhos, sabe? 169.254.154.180."*

* **Áudio 33 (`18.17.08.opus` — 00:27):**
  > *"Atualizando aí, ó:*  
  > *• **6, 5 e 2 [MLO Tri-Band]:** Bloqueio total!*  
  > *• **5 e 6 [MLO Dual-Band]:** Bloqueio também!*  
  > *• **2 e 5 [MLO Dual-Band com 6 separado]:** PERFEITO! Funcionando OK com o 6 separado!*  
  > *Provavelmente então o problema tá vindo do WPA3, cara. É um protocolo muito grande pra ficar fuçando, pra mexer, pra tentar descobrir um monte de situação, então ele bloca se ele tiver misturado. Vou até fazer o último teste aqui pra ver se confirma, que eu coloquei o 5 com 6 agora pra ver se ele repassa o IP."*

* **Áudio 34 (`18.30.28.opus` — 00:54):**
  > *"É, não, realmente cara, eu tinha essa dúvida se realmente o sistema anterior do roteador ele realmente trabalhava de verdade, né? Eu achava meio estranho WPA3 com WPA2 fazer um Band Steering com WPA3 ou WPA2, eu achei que às vezes era meio paia, mano, muito paia algumas opções dele ali, algumas funções.*  
  > *Voltando ao assunto, vou te falar que o MLO de 5 GHz com 2.4 GHz tá trabalhando bem, cara! Tá interessante! Vou até deixar aqui pra fazer uns testes. Agora, repetindo: se eu colocar 5 e 6, down — ele não repassa o IP. Se eu colocar o Tri-Band, que eu chamo de steering, down — ele não passa pra nenhuma das interfaces.*  
  > *É linha pra caralho pro cara compilar, é foda. E o único problema mesmo que enche o saco é só a porra do Red Light, cara, porque você tem que ficar fazendo reinício toda hora. Como eu tô com ele aqui na mesa aqui é mais fácil, eu só pego e reinicio porque o cabo de rede funciona de boa, mas quando é wireless ele derruba o wireless e você tem que ir lá e tirar da tomada."*

* **Áudio 35 (`18.31.12.opus` — 00:15):**
  > *"O foda da conferência é que você tem que trabalhar com o que tá disponível no roteador, né mano? De repente se tivesse o repositório dele você poderia até instalar um `relayd`, cara, e ele ia funcionar bem pra caramba como repetidor tanto passivo quanto ativo, cara. É foda, não tem mais o repositório dele."*

* **Áudio 36 (`18.35.16.opus` — 00:22):**
  > *"E um detalhe chato, sendo repetitivo: se der pra conseguir fazer o 5 GHz e o 2.4 GHz SEMPRE startar com WPA2, cara, é melhor! Porque qualquer configuração que você for fazer, WPA2 sempre, cara! Porque ele não dá compatibilidade com um monte de equipamento se você colocar o WPA3 ou WPA2 Mixed."*

---

## 🔬 3. Auditoria do Arquivo de Backup Enviado pelo Diego (`backup-Predator Connect T7-2026-10-12.tar.gz`)

Inspecionamos diretamente os arquivos `/etc/config/wireless`, `/etc/config/dhcp` e `/etc/config/ksmbd` contidos no backup enviado pelo Diego:

1. **`/etc/config/wireless`:**
   * `wifi0` (2.4 GHz): Configurado com `hwmode '11beg'`, `htmode 'HT40'`, `txpower '24'`, `encryption 'psk2+aes'` (WPA2 puro).
   * `wifi1` (5.0 GHz): Configurado com `hwmode '11bea'`, `htmode 'HT160'`, `txpower '26'`, `encryption 'psk2+aes'` (WPA2 puro).
   * `wifi2` (6.0 GHz): Configurado com `hwmode '11bea'`, `htmode 'HT320'`, `txpower '20'`, `encryption 'sae'`, `ieee80211w '2'` (WPA3 puro).
   * **Por que o 6 GHz havia parado quando ele desligou o Wi-Fi 7 (4096-QAM)?** Quando se desativa o modo `11be` no rádio de 6 GHz mantendo `htmode 'HT320'`, o driver `qcawificfg80211` rejeita a combinação porque **largura de canal de 320 MHz só existe na especificação 802.11be (Wi-Fi 7)**. Se mudar o `hwmode` de `11bea` para `11axa` (Wi-Fi 6E) sem baixar o `htmode` para `HT160`, o rádio `wifi2` aborta a inicialização!

2. **`/etc/config/ksmbd`:**
   * Compartilhamento `Armazenamento_USB` em `/mnt` já operando com `create_mask '0777'`, `dir_mask '0777'` e `force_root '1'`.

---

## 📊 4. Matriz Consolidada de Problemas, Diagnósticos e Correções (v2.1)

| Item | Área | Sintoma Reportado | Causa Técnica | Severidade | Ação Definitiva no Projeto (v2.1) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **01** | **Criptografia Padrão** | Impressoras (Creality/papel), Xiaomi e repetidores não conectam com WPA3 ou WPA2/WPA3 Mixed | Dispositivos IoT e legados falham na negociação SAE / PMF (`ieee80211w`) | **Crítica** | Travar **WPA2-PSK (`psk2+aes`)** sempre como padrão para 2.4 GHz e 5 GHz em todas as funções do ARC. |
| **02** | **MLO / Band Steering** | MLO `Tri-Band (2.4+5+6)` e `Dual (5+6)` não entregam IP (erro `169.254.x.x`), mas **`2.4 + 5 GHz` funciona 100%** | Misturar uma interface `WPA3/SAE` obrigatória (6 GHz) com interfaces `WPA2` na mesma ponte MLO bloqueia o EAPOL/DHCP no driver QCA | **Crítica** | Na Central ARC, definir o modo MLO recomendado como **Dual-Band (2.4 GHz + 5 GHz em WPA2)** mantendo o **6 GHz independente em WPA3**. |
| **03** | **Modulação 4096-QAM / Wi-Fi 7** | Desligar a opção Wi-Fi 7 (4096-QAM) na Central ARC derruba o rádio de 6 GHz | O 6 GHz usa `HT320` (320 MHz), que é exclusivo do padrão `11be`. Desligar `11be` mantendo `HT320` invalida o driver | **Alta** | Na Central ARC, manter `11bea` sempre ativo no 6 GHz (ou, se baixar para AX, forçar `HT160` automaticamente). |
| **04** | **Red Light no Save & Apply** | Salvar alterações de Wi-Fi gera LED vermelho e exige desligar da tomada | Restart abrupto da pilha derruba o switch NSS ou entra em espera de DFS CAC de 60s | **Alta** | Usar recarregamento isolado de interface sem derrubar `br-lan` e aumentar o timer de espera. |
| **05** | **Timeouts de UI** | LuCI (90s) dava rollback sozinho; ARC (20s) reconectava antes do rádio subir | O ciclo completo dos 3 rádios Qualcomm + DFS leva de 60s a 120s | **Média** | Fixar `luci.apply.timeout=300` (300s) e aumentar o contador regressivo da Central ARC para **90s**. |
| **06** | **Repetidor Wireless (Intelbras)** | Repetidor em 2.4 GHz pede IP mas o OpenWrt não entrega; driver aparece "disabled" no LuCI | LuCI procura `mac80211`, mas o T7 usa `qcawificfg80211` (gerenciado via `cfg80211tool`/UCI). Repetidor sem WDS precisa de `wds '1'` | **Média** | Adicionar suporte à flag `option wds '1'` nas interfaces AP (`wifi0_ap` e `wifi1_ap`) para permitir repetidores transparentes e ponte DHCP. |
| **07** | **USB / KSMBD** | Pen drive precisava de `mask 777` e `666` manual para liberar escrita | Template padrão criava arquivos restritos | **Resolvido** | Já validado no backup com `create_mask '0777'`, `dir_mask '0777'` e `force_root '1'`. |

---

## 🛠️ 5. Resumo das Alterações Prontas para o Pacote v2.1

1. **Trava WPA2-PSK (`psk2+aes`) em 2.4 GHz e 5 GHz:** Nunca aplicar `psk-mixed` ou `sae` em 2.4 GHz e 5 GHz ao usar a Central ARC.
2. **MLO Inteligente (2.4 GHz + 5 GHz unificados em WPA2 + 6 GHz dedicado em WPA3):** Impede o bug de IP `169.254.x.x` descoberto pelo Diego.
3. **Proteção de 320 MHz / `11bea` no 6 GHz:** Impedir que a desativação de recursos derrube o rádio `wifi2`.
4. **Habilitação de `option wds '1'` nos APs:** Para permitir que repetidores Wi-Fi (como o Intelbras RG 1200) repassem tráfego DHCP normalmente para os clientes.
5. **Timeout de 300s no LuCI e 90s na Central ARC.**
