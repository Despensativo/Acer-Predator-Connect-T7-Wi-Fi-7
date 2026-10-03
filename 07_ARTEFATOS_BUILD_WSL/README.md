# Frente de Desenvolvimento — Feito por ChatGPT

Esta pasta reúne as ferramentas, compiladores e diagnósticos desenvolvidos para o Acer Predator Connect T7.

---

## 📌 Documentação Ativa

1. [**STATUS_SLOTS_E_BOOT_T7.md**](STATUS_SLOTS_E_BOOT_T7.md)
   - Consolidação técnica sobre Slot 1 (OEM/ativo) vs Slot 2 (teste/inativo).
   - Funcionamento de `/usr/sbin/boot-openwrt` e `/usr/sbin/boot-acer`.
   - Procedimentos de teste em RAM via TFTP (`192.168.1.66` / `0x41000000`).
   - Requisitos de autenticação Qualcomm TrustZone SCM / WCSS.

2. [**COMPILADOR-OFICIAL-SQUASHFS-T7/v1.0**](COMPILADOR-OFICIAL-SQUASHFS-T7/v1.0/LEIA-PRIMEIRO.md)
   - Compilador de referência `mksquashfs-qsdk` validado para o T7.
   - [Procedimento de compilação e teste](COMPILADOR-OFICIAL-SQUASHFS-T7/v1.0/PROCEDIMENTO.md).
   - [Documentação técnica de compatibilidade](COMPILADOR-OFICIAL-SQUASHFS-T7/v1.0/documentacao/MKSQUASHFS-COMPATIVEL-ACER-2026-10-02.md).

---

## 🗄️ Histórico de Sessões

Os relatórios intermediários diários (gerados entre 02/10 e 03/10/2026) foram arquivados em [**`_archive_historico/`**](_archive_historico/) para evitar duplicação e consumo excessivo de contexto de IA.
