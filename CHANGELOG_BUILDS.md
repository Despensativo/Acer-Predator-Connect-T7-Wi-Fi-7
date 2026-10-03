# Histórico e Matriz de Builds — Acer Predator Connect T7

> Registro consolidado de compilações, testes em RAM e gravações de RootFS no Acer Predator Connect T7.

---

## 1. Matriz de Versões e Status de Testes

| Build ID | Data | Alvo | Kernel | Componentes | Status do Boot | Observações / Resultado |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`v0.1-diag`** | 02/10/2026 | RAM (FIT) | Linux 6.18.52 | Initramfs estático mínimo C | ⚠️ Compilado Offline | Sem drivers de rede; teste de hardware pendente. |
| **`v0.2-diag`** | 02/10/2026 | RAM (FIT) | Linux 6.18.52 | Netconsole + UDP heartbeat | ⚠️ Compilado Offline | Adicionados patches de Ethernet IPQ5332. |
| **`v0.3-diag`** | 02/10/2026 | RAM (FIT) | Linux 6.18.52 | Sonda U-Boot + 7 patches rede | ⚠️ Compilado Offline | Carga em `0x41000000`, tamanho FIT 3.34 MiB. |
| **`v1.0-mod-cfg`** | 02/10/2026 | Flash (Stock) | Linux 5.4 OEM | Dropbear + Telnet via `.cfg` |  **SUCESSO TOTAL** | Portas 22 e 23 abertas, acesso root ativo. |
| **`v1.1-luci-mod`**| 02/10/2026 | Flash (Stock) | Linux 5.4 OEM | LuCI porta 8080 + Debloat |  **SUCESSO TOTAL** | Interface LuCI 100% funcional + FOTA desativado. |
| **`v2.0-slot2-cand`**| 03/10/2026 | Slot 2 (`mtd20`)| Linux 5.4 OEM | SquashFS custom 256k XZ | 🔄 Preparado | Retorno ao Slot 1 validado e pronto para ensaio. |

---

## 2. Parâmetros dos Candidatos em RAM (Compilados em WSL)

- **Candidato v3**: `07_ARTEFATOS_BUILD_WSL/artefatos/t7-net-20261002-v3/t7-arm64-diag-CANDIDATO-NAO-ENVIAR.itb`
  - **Tamanho FIT**: 3.503.744 bytes (~3,34 MiB)
  - **SHA-256**: `0d5a9205cfdcafc34004ed8dc94973a54c1e0c367db8efac4177026ff2caaed9`
  - **Endereço de Carga RAM**: `0x41000000`
  - **Toolchain**: GCC 14.4.0 AArch64 / musl

---

## 3. Parâmetros do Compilador de RootFS (SquashFS QSDK)

- **Versão**: `05_COMPILADORES/SquashFS_QSDK_T7/v1.0`
- **Comando Padrão**:
  ```bash
  ./mksquashfs rootfs_dir out.bin -b 256k -comp xz -noappend -all-root
  ```
- **Round-Trip Test**: 100% verificado contra a extração do binário de fábrica da Acer.
