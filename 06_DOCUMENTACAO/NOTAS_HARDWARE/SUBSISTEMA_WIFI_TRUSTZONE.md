# Subsistema Wi-Fi, Qualcomm TrustZone e Q6 WCSS — IPQ5332

> **Resumo Técnico**: Este documento detalha a arquitetura de segurança da Qualcomm para o SoC IPQ5332 (Miami) presente no Acer Predator Connect T7 e as dependências para habilitar os rádios Wi-Fi em kernels novos (Linux 6.x) ou OpenWrt upstream.

---

## 1. Arquitetura de Isolamento de Rádio

No Qualcomm IPQ5332, o subsistema de rádio sem fio (WCSS - *Wireless Connectivity Subsystem*) não é controlado diretamente por drivers monolíticos do kernel Linux em modo Kernel/EL1.
Em vez disso:
1. O rádio roda sobre um processador Hexagon DSP (Q6).
2. O firmware binário do Q6 (`q6_fw.mdt`, `wcss.bin`) é segmentado e assinado criptograficamente.
3. O kernel Linux **não tem permissão de carregar o firmware diretamente no hardware**: ele precisa solicitar a inicialização à camada de segurança **Qualcomm TrustZone (SCM / EL3)**.

---

## 2. Requisitos de Autenticação SCM e PIL

Para que o Linux consiga acordar os rádios Wi-Fi 7:
- **Driver Obrigatório**: `drivers/remoteproc/qcom_q6v5_wcss_sec.c`
- **Config do Kernel**: `CONFIG_QCOM_Q6V5_WCSS_SEC=y`
- **Device Tree Node Compatible**: `qcom,ipq5332-wcss-sec-pil`
- **ID de Peripheral Authentication Service (PAS ID)**: `0xd` (13 decimal)
- **Subsystem Name**: `q6wcss`

### Fluxo de Inicialização:
1. O driver PIL lê os cabeçalhos ELF/MDT do firmware em `/lib/firmware/`.
2. O driver faz a chamada SCM segura: `qcom_scm_pas_init_image(0xd, metadata)`.
3. A TrustZone verifica a assinatura de hardware da Acer/Qualcomm.
4. Após aprovação, o kernel chama `qcom_scm_pas_auth_and_reset(0xd)`.
5. O coprocessador Q6 é liberado do reset e os rádios iniciam a calibração com base na partição `ART` (`mtd18`).

---

## 3. Comparativo de Compatibilidade por Kernel

| Kernel | Suporte Wi-Fi 7 / MLO | Suporte NSS / PPE | Estado no Acer T7 |
| :--- | :--- | :--- | :--- |
| **Linux 5.4 (Qualcomm QSDK OEM)** | **100% Funcional** (Nativo) | **Aceleração via Hardware (0% CPU)** | **Recomendado para produção e uso diário** |
| **Linux 6.18 (ImmortalWrt / Upstream)** | Parcial / Requer patches SCM | Aceleração básica por software | Em desenvolvimento experimental |

> [!TIP]
> Para obter a melhor performance de rede (2.5 Gbps sem saturação de CPU) e estabilidade de Wi-Fi 7, a abordagem mais segura e eficiente é utilizar o **RootFS OpenWrt LuCI modificado rodando sobre o kernel 5.4 OEM**.
