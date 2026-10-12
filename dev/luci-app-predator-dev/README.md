# Addon LuCI Modo DEV & Fail-Safe Dual-Boot (Acer Predator Connect T7)

Este pacote adiciona salvaguardas profissionais de desenvolvimento, proteção contra bootloop entre partições e telemetria forense completa ao Acer Predator Connect T7.

---

## 🚀 Funcionalidades Principais

### 1. Fail-Safe Anti-Bootloop Inteligente (Dual-Boot Automático)
- **Watchdog Precoce (`START=01`)**: Roda no início absoluto do boot, antes dos subsistemas de rede e wireless.
- **Contador Persistente**: Armazena falhas de boot consecutivas em `/data/boot_fail_count`.
- **Janela de Confirmação Saudável**: Se o roteador operar por 75 segundos com estabilidade, o contador é zerado automaticamente.
- **Failover Automático**: Se o sistema reiniciar ou travar antes dos 75s por **X tentativas** (padrão: 3), o script inverte o `primaryboot` em `0:BOOTCONFIG` e `0:BOOTCONFIG1` e força a inicialização imediata na partição oposta saudável.

### 2. Registro Persistente de Logs de Boot (Retenção por até 7 Dias)
- **Captura Forense Completa**:
  - `dmesg` do kernel (barramento PCIe, MHI, WCSS, chips Qualcomm).
  - `logread` (syslog de todos os serviços).
  - `/dev/mtd23` (`0:SYSTRACE` via `mtdoops`) - dumps físicos de pânicos anteriores.
  - Interfaces Wi-Fi 7 (`iw dev`), memória (`free -m`) e armazenamento (`df -h`).
- **Compactação GZIP**: Reduz o tamanho de cada boot para apenas **~35 KB**.
- **Limpeza Automática**: Expurga logs com mais de 7 dias automaticamente.
- **Espaço Seguro**: Usa `/data/boot_logs/` na partição de dados (`rootfs_data`), ocupando menos de 2% dos 138 MB disponíveis.

### 3. Interface Gráfica Integrada no LuCI
- Menu: **Sistema -> Modo DEV & Fail-Safe**.
- Badge visual do Slot ativo (Slot 1 ou Slot 2).
- Monitor do contador de falhas em tempo real.
- Botão **[📥 Baixar Todos os Logs (.tar.gz)]** com download em 1 clique.
- Botão **[📄 Ver Último Log de Boot]** com visualizador monospace embutido.
- Botão **[🔄 Zerar Contador de Falhas]**.
- Botão **[🔀 Alternar Partição Agora]** com confirmação modal.

### 4. Linha de Comando (CLI)
- Utilitário `/usr/sbin/predator-dev`:
  ```sh
  predator-dev status          # Exibe status completo, slot ativo e logs
  predator-dev view latest     # Exibe o último log de boot no terminal
  predator-dev pack            # Empacota todos os logs em um .tar.gz
  predator-dev reset           # Zera o contador de falhas
  predator-dev switch          # Alterna de partição manualmente
  predator-dev clean           # Remove todos os logs
  ```
