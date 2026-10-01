# Manual Técnico: Modo de Recuperação e Boot por RAM — Acer Predator Connect T7

Este documento registra a análise de engenharia reversa do bootloader oficial (**U-Boot 2.0 versão `25.01.17`**, Qualcomm IPQ5332 Hawkeye) do roteador **Acer Predator Connect T7**, detalhando o procedimento de entrada/saída do modo de recuperação web e a mecânica de execução em memória RAM.

---

## 1. Modo de Recuperação de Fábrica (Pepe2k Web Failsafe)

O bootloader do Predator Connect T7 contém uma versão personalizada do servidor HTTP de recuperação Pepe2k (`uIP/0.9`).

### Como Entrar no Web Failsafe
1. Desconecte a fonte de alimentação do roteador da tomada.
2. Mantenha pressionado o botão físico **WPS** na carcaça (conectado internamente ao **GPIO 35**).
3. Plugue a fonte na tomada mantendo o botão pressionado.
4. Mantenha pressionado por **5 segundos** (o U-Boot requer no mínimo 3 segundos contínuos para abortar a inicialização normal).
5. Solte o botão. O roteador suspende o boot e inicia o servidor web em:
   * **URL:** `http://192.168.1.1`
   * **Porta de conexão:** **LAN 1** (Game port)
   * **IP do computador:** Deve estar configurado manualmente na faixa `192.168.1.x` (ex: `192.168.1.5`, máscara `255.255.255.0`).

### Regras Críticas do Web Failsafe (Engenharia Reversa)
* **Trava de Tamanho Mínimo (10 KB):** No endereço `0x4a439af6` do binário `appsbl.bin`, o código valida `cmp r3, #10240`. Se qualquer arquivo enviado tiver menos de 10 KB, a conexão é encerrada imediatamente sem cabeçalhos HTTP, gerando no navegador o erro `NS_ERROR_NET_EMPTY_RESPONSE`. Qualquer script ou imagem enviada por essa interface **deve ter mais de 10.240 bytes**.
* **Comportamento de Reset:** Toda operação concluída com sucesso pelo Web Failsafe chama incondicionalmente a rotina `do_reset()` (`0x4a402460`), reiniciando a placa.
* **Perigo da Gravação Automática de NAND:** O manipulador de UBI (`Type 3`) do failsafe executa:
  ```sh
  nand erase 0xa00000 0x7300000; nand write 0x44000000 0xa00000 <tamanho>
  ```
  No Predator T7, o endereço `0xa00000` coincide com a área de bootloaders auxiliares e o próprio U-Boot (`0x1100000`). Gravar imagens brutas por esse método causaria corrupção do bootloader.

---

## 2. Como Restaurar as Variáveis e Sair para a Acer Original

Para restaurar o comando de boot de fábrica caso o roteador não inicialize automaticamente:

1. Baixe o arquivo **`restaurar_acer.itb`** (gerado com padding de 33 KB para superar a trava de 10 KB).
2. Acesse a tela em `http://192.168.1.1`.
3. Selecione o arquivo e clique em **Update firmware**.
4. O interpretador executa o script interno:
   ```sh
   setenv bootcmd bootipq
   saveenv
   bootipq
   ```
5. O U-Boot restaura `bootcmd=bootipq`, persiste na partição `mtd13` (`0:APPSBLENV`), e inicializa imediatamente o firmware oficial da Acer (painel web original em `http://192.168.76.1`).

---

## 3. Por Que o Modo RAM Só Roda com Sucesso via TFTP?

Sua observação técnica foi **100% precisa**. Existe uma diferença fundamental de arquitetura entre a página web e o TFTP:

```
[ PÁGINA WEB (Failsafe) ]
Upload via HTTP -> Memória RAM (0x44000000) -> Conclusão -> Chama do_reset() -> Reinicia
                                                                     ↓
                                                       A memória RAM é limpa!

--------------------------------------------------------------------------------------

[ BOOT VIA TFTP (tftpboot) ]
U-Boot liga -> tftpboot 0x44000000 openwrt.itb -> bootm 0x44000000 -> Pula direto pro Linux
                                                                            ↓
                                                                 NÃO reinicia a placa!
                                                                 OpenWrt roda 100% na RAM!
```

### Por que o TFTP anterior não tinha subido?
1. **Porta errada:** Estava na WAN (PHY 2.5G que demorava 22 segundos para dar link elétrico, enquanto o U-Boot esperava apenas 3 segundos). Na porta **LAN 1**, o link sobe em menos de 1 segundo.
2. **Endereço do Servidor:** O U-Boot da Acer força `serverip=192.168.10.10` e `ipaddr=192.168.10.1`.
3. Quando o U-Boot não encontrou o arquivo na rede, o comando foi abortado antes de repassar para o `bootipq`.

---

## 4. Resumo de Segurança
* O roteador possui dupla proteção: partição `0:APPSBL` protegida e failsafe físico no botão WPS.
* Nenhuma gravação destrutiva foi feita na flash; o firmware original da Acer permanece preservado.
