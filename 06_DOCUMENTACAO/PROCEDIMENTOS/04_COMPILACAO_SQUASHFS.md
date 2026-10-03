# Procedimento 04: Descompactação e Compilação de SquashFS

> **Status:** [VALIDADO EM AMBIENTE WSL/LINUX]  
> **Nível de Risco:** [NENHUM NA GERAÇÃO | CRÍTICO NO FLASH]  
> **Objetivo:** Extrair o RootFS original e recompilar imagens SquashFS com compatibilidade total para o kernel e U-Boot do Acer T7.

---

## 1. Ferramentas Necessárias

Utilize o pacote compilado e validado em:
`05_COMPILADORES/SquashFS_QSDK_T7/v1.0/`

- **Binários**: `mksquashfs` e `unsquashfs` (derivados do Qualcomm QSDK).
- **Dependências no Ubuntu/Debian/WSL**:
  ```bash
  sudo apt-get update && sudo apt-get install -y liblzma-dev zlib1g-dev build-essential
  ```

---

## 2. Descompactação do RootFS Original

```bash
# Extrair o conteúdo preservando proprietários e permissões:
sudo ./unsquashfs -d rootfs_extraido rootfs_original.bin
```

---

## 3. Aplicação das Modificações

Faça as edições desejadas dentro da pasta `rootfs_extraido/`:
- Injeção de chaves SSH em `etc/dropbear/`
- Customização de scripts em `etc/init.d/` ou `etc/rc.local`
- Adição de arquivos de configuração

---

## 4. Recompilação Compatível (Comando Obrigatório)

Para que o U-Boot e o kernel aceitem a partição sem falhas de montagem UBI:

```bash
sudo ./mksquashfs rootfs_extraido rootfs_custom.bin \
    -b 256k \
    -comp xz \
    -noappend \
    -all-root \
    -processors 4
```

### Parâmetros Críticos:
| Parâmetro | Motivo |
| :--- | :--- |
| `-b 256k` | Bloco de 256 KiB (262.144 bytes), obrigatório para a geometria NAND/UBI do T7. |
| `-comp xz` | Compressão XZ correspondente ao descompressor embutido no kernel OEM. |
| `-all-root` | Garante que todos os arquivos pertençam a `root:root` (UID/GID 0). |
| `-noappend` | Sobrescreve o arquivo de saída em vez de anexar. |

---

## 5. Validação de Tamanho e Hash

Antes de enviar ao roteador:
```bash
# 1. Conferir tamanho (não pode ultrapassar o tamanho máximo da partição MTD de 80 MB):
ls -lh rootfs_custom.bin

# 2. Gerar hash SHA-256 de validação:
sha256sum rootfs_custom.bin
```
