#!/usr/bin/env python3
"""
Construtor do Kernel FIT Mainline ARM64 com Ramoops (Pstore) e UARTDM Real
Acer Predator Connect T7 (IPQ5322)
"""

import subprocess
import os
import sys

BASE_DIR = r"h:\FEITOS COM IA\Acer-Predator-Connect-T7"
OUT_DIR = os.path.join(BASE_DIR, "1 - Firmware e Imagens OpenWrt")
OUT_FIT = os.path.join(OUT_DIR, "openwrt-predator-t7-kernel-ramoops.fit")

WSL_SRC_FIT = "/mnt/h/FEITOS COM IA/Acer-Predator-Connect-T7/1 - Firmware e Imagens OpenWrt/openwrt-predator-t7-kernel-arm64.fit"
WSL_WORK_DIR = "/tmp/fit_ramoops_build"
WSL_OUT_FIT = "/mnt/h/FEITOS COM IA/Acer-Predator-Connect-T7/1 - Firmware e Imagens OpenWrt/openwrt-predator-t7-kernel-ramoops.fit"

def run_wsl(cmd):
    p = subprocess.run(["wsl", "bash", "-c", cmd], capture_output=True, text=True)
    if p.returncode != 0:
        print(f"[-] Erro WSL: {p.stderr}")
        return False, p.stderr
    return True, p.stdout

def main():
    print("=" * 70)
    print("CONSTRUINDO KERNEL FIT ARM64 COM RAMOOPS (PSTORE)")
    print("Acer Predator Connect T7 (IPQ5322)")
    print("=" * 70)

    # 1. Preparar diretorio
    print("[*] Etapa 1: Extraindo componentes do FIT ARM64 existente...")
    run_wsl(f"rm -rf {WSL_WORK_DIR} && mkdir -p {WSL_WORK_DIR}")

    # Extrai kernel e DTB
    cmd_ext = f"cd {WSL_WORK_DIR} && dumpimage -T flat_dt -p 0 -o kernel-1.lzma '{WSL_SRC_FIT}' && dumpimage -T flat_dt -p 1 -o fdt-1.dtb '{WSL_SRC_FIT}' && dtc -I dtb -O dts -o fdt-1.dts fdt-1.dtb 2>/dev/null"
    ok, out = run_wsl(cmd_ext)
    if not ok:
        print("[-] Falha ao extrair FIT.")
        return 1

    # 2. Ler DTS no Windows e modificar
    print("[*] Etapa 2: Injetando nó ramoops@4cc00000 e bootargs com earlycon UARTDM real...")
    # Copia fdt-1.dts temporariamente para o Windows
    temp_dts_win = os.path.join(OUT_DIR, "temp_fdt.dts")
    run_wsl(f"cp {WSL_WORK_DIR}/fdt-1.dts '/mnt/h/FEITOS COM IA/Acer-Predator-Connect-T7/1 - Firmware e Imagens OpenWrt/temp_fdt.dts'")

    with open(temp_dts_win, "r", encoding="utf-8") as f:
        dts = f.read()

    # Atualizar bootargs
    old_bootargs_start = dts.find('bootargs = "')
    if old_bootargs_start != -1:
        old_bootargs_end = dts.find('";', old_bootargs_start)
        new_bootargs = 'bootargs = "console=ttyMSM0,115200n8 earlycon=msm_serial_dm,0x078af000 maxcpus=1 nowatchdog panic=0 ubi.mtd=rootfs_1 root=mtd:ubi_rootfs rootfstype=squashfs rootwait";'
        dts = dts[:old_bootargs_start] + new_bootargs + dts[old_bootargs_end+2:]

    # Inserir ramoops em reserved-memory apos 'ranges;'
    ramoops_snippet = (
        "\n\t\tramoops@4cc00000 {\n"
        "\t\t\tcompatible = \"ramoops\";\n"
        "\t\t\treg = <0x00 0x4cc00000 0x00 0x100000>;\n"
        "\t\t\trecord-size = <0x20000>;\n"
        "\t\t\tconsole-size = <0x40000>;\n"
        "\t\t\tpmsg-size = <0x20000>;\n"
        "\t\t};\n"
    )
    idx = dts.find("reserved-memory {")
    if idx != -1:
        ranges_idx = dts.find("ranges;", idx)
        if ranges_idx != -1:
            end_ranges = ranges_idx + len("ranges;")
            dts = dts[:end_ranges] + ramoops_snippet + dts[end_ranges:]

    temp_ramoops_dts_win = os.path.join(OUT_DIR, "temp_ramoops.dts")
    with open(temp_ramoops_dts_win, "w", encoding="utf-8") as f:
        f.write(dts)

    # Copiar de volta e compilar DTB
    run_wsl(f"cp '/mnt/h/FEITOS COM IA/Acer-Predator-Connect-T7/1 - Firmware e Imagens OpenWrt/temp_ramoops.dts' {WSL_WORK_DIR}/fdt-ramoops.dts")
    ok, out = run_wsl(f"dtc -I dts -O dtb -o {WSL_WORK_DIR}/fdt-ramoops.dtb {WSL_WORK_DIR}/fdt-ramoops.dts 2>/dev/null")
    if not ok:
        print("[-] Falha ao compilar DTB com dtc.")
        return 1

    # Limpar arquivos temporarios no Windows
    if os.path.exists(temp_dts_win): os.remove(temp_dts_win)
    if os.path.exists(temp_ramoops_dts_win): os.remove(temp_ramoops_dts_win)

    # 3. Criar arquivo ITS
    print("[*] Etapa 3: Criando descritor ITS...")
    its_lines = [
        "/dts-v1/;",
        "/ {",
        '    description = "ARM64 Mainline Linux Kernel 6.18 with Ramoops for Acer Predator T7";',
        "    #address-cells = <1>;",
        "    images {",
        "        kernel-1 {",
        '            description = "ARM64 Linux Kernel 6.18";',
        f'            data = /incbin/("{WSL_WORK_DIR}/kernel-1.lzma");',
        '            type = "kernel";',
        '            arch = "arm64";',
        '            os = "linux";',
        '            compression = "lzma";',
        "            load = <0x41000000>;",
        "            entry = <0x41000000>;",
        "            hash-1 {",
        '                algo = "crc32";',
        "            };",
        "            hash-2 {",
        '                algo = "sha1";',
        "            };",
        "        };",
        "        fdt-1 {",
        '            description = "Acer Predator Connect T7 Device Tree with Ramoops";',
        f'            data = /incbin/("{WSL_WORK_DIR}/fdt-ramoops.dtb");',
        '            type = "flat_dt";',
        '            arch = "arm64";',
        '            compression = "none";',
        "            hash-1 {",
        '                algo = "crc32";',
        "            };",
        "            hash-2 {",
        '                algo = "sha1";',
        "            };",
        "        };",
        "    };",
        "    configurations {",
        '        default = "config@mi01.6";',
        '        config@mi01.6 {',
        '            description = "OpenWrt Linux ARM64 with Ramoops Diagnostic";',
        '            kernel = "kernel-1";',
        '            fdt = "fdt-1";',
        "        };",
        "    };",
        "};"
    ]
    its_content = "\n".join(its_lines)
    its_win_path = os.path.join(OUT_DIR, "temp_ramoops.its")
    with open(its_win_path, "w", encoding="utf-8") as f:
        f.write(its_content)

    run_wsl(f"cp '/mnt/h/FEITOS COM IA/Acer-Predator-Connect-T7/1 - Firmware e Imagens OpenWrt/temp_ramoops.its' {WSL_WORK_DIR}/kernel_ramoops.its")
    if os.path.exists(its_win_path): os.remove(its_win_path)

    # 4. Compilar FIT com mkimage
    print("[*] Etapa 4: Compilando imagem FIT com mkimage...")
    cmd_mk = f"cd {WSL_WORK_DIR} && mkimage -f kernel_ramoops.its '{WSL_OUT_FIT}' > /dev/null"
    ok, out = run_wsl(cmd_mk)
    if not ok:
        print("[-] Falha ao executar mkimage.")
        return 1

    # 5. Limpeza
    run_wsl(f"rm -rf {WSL_WORK_DIR}")

    if os.path.exists(OUT_FIT):
        sz = os.path.getsize(OUT_FIT)
        print("\n" + "=" * 70)
        print("[SUCESSO] KERNEL FIT COM RAMOOPS GERADO COM SUCESSO!")
        print(f"Arquivo: {OUT_FIT}")
        print(f"Tamanho: {sz} bytes ({sz / (1024*1024):.2f} MB)")
        print("=" * 70)
        return 0
    else:
        print("[-] Arquivo FIT final nao encontrado.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
