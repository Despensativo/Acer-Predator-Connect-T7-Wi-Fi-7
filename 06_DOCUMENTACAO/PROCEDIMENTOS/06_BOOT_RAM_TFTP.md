# Procedimento 06: Teste e Boot em RAM via TFTP

> **Status:** [IMAGENS COMPILADAS OFFLINE / TESTE EM BANCADA PENDENTE]  
> **Nível de Risco:** [MUITO BAIXO - Zero escrita na memória Flash]  
> **Objetivo:** Inicializar uma imagem de diagnóstico diretamente na memória RAM via rede (TFTP), sem modificar nenhuma partição NAND do roteador.

---

## 1. Parâmetros de Rede

- **IP do Computador (Servidor TFTP):** `192.168.1.66` (Máscara `255.255.255.0`)
- **IP do Roteador:** `192.168.1.1`
- **Endereço de Carga RAM (Load Address):** `0x41000000`
- **Porta LAN:** Conectar o cabo na porta **LAN 1** (2.5 Gbps ou 1 Gbps)

---

## 2. Preparação do Servidor TFTP no Windows

1. Configure o IP da placa de rede do Windows:
   - IP: `192.168.1.66`
   - Máscara: `255.255.255.0`
   - Gateway: deixar em branco ou `192.168.1.1`
2. Abra o software TFTP (ex.: *Tftpd64* localizado em `Servidor_TFTP_Windows/`).
3. Aponte o diretório base para a pasta que contém o arquivo FIT (`.itb`).

---

## 3. Disparo do Boot em RAM via U-Boot (UART Console)

No terminal serial (115200 8N1):

```sh
# 1. Configurar variáveis de rede no U-Boot:
setenv ipaddr 192.168.1.1
setenv serverip 192.168.1.66

# 2. Carregar a imagem FIT para a memória RAM:
tftpboot 0x41000000 t7-arm64-diag.itb

# 3. Executar o boot diretamente da RAM:
bootm 0x41000000
```

> [!NOTE]
> Se o roteador reiniciar ou travar durante a execução em RAM, basta desligar da tomada e ligar novamente. A memória Flash não é alterada e o roteador subirá normalmente no firmware original.
