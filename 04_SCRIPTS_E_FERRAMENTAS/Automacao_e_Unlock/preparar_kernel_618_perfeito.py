import subprocess
import os
import sys

BASE_DIR = r"h:\FEITOS COM IA\Acer-Predator-Connect-T7"
OUT_DIR = os.path.join(BASE_DIR, "1 - Firmware e Imagens OpenWrt")
OUT_FIT = os.path.join(OUT_DIR, "openwrt-predator-t7-kernel-618-final.fit")

WSL_SRC_FIT = "/mnt/h/FEITOS COM IA/Acer-Predator-Connect-T7/1 - Firmware e Imagens OpenWrt/openwrt-predator-t7-kernel-arm64.fit"
WSL_WORK_DIR = "/tmp/fit_618_final_build"
WSL_OUT_FIT = "/mnt/h/FEITOS COM IA/Acer-Predator-Connect-T7/1 - Firmware e Imagens OpenWrt/openwrt-predator-t7-kernel-618-final.fit"

def run_wsl(cmd):
    p = subprocess.run(["wsl", "bash", "-c", cmd], capture_output=True, text=True)
    if p.returncode != 0:
        print(f"[-] Erro WSL: {p.stderr}")
        return False, p.stderr
    return True, p.stdout

def main():
    print("=" * 70)
    print("CONSTRUINDO KERNEL FIT 6.18 ARM64 COM BOOTARGS PERFEITOS")
    print("Acer Predator Connect T7 (IPQ5322)")
    print("=" * 70)

    run_wsl(f"rm -rf {WSL_WORK_DIR} && mkdir -p {WSL_WORK_DIR}")

    # Extrai kernel e DTB
    cmd_ext = f"cd {WSL_WORK_DIR} && dumpimage -T flat_dt -p 0 -o kernel-1.lzma '{WSL_SRC_FIT}' && dumpimage -T flat_dt -p 1 -o fdt-1.dtb '{WSL_SRC_FIT}' && dtc -I dtb -O dts -o fdt-1.dts fdt-1.dtb 2>/dev/null"
    ok, out = run_wsl(cmd_ext)
    if not ok:
        print("[-] Falha ao extrair FIT original.")
        return 1

    temp_dts_win = os.path.join(OUT_DIR, "temp_fdt618.dts")
    run_wsl(f"cp {WSL_WORK_DIR}/fdt-1.dts '/mnt/h/FEITOS COM IA/Acer-Predator-Connect-T7/1 - Firmware e Imagens OpenWrt/temp_fdt618.dts'")

    with open(temp_dts_win, "r", encoding="utf-8") as f:
        dts = f.read()

    # Atualizar bootargs com ubi.mtd=rootfs (e nao rootfs_1!) e earlycon correto
    old_bootargs_start = dts.find('bootargs = "')
    if old_bootargs_start != -1:
        old_bootargs_end = dts.find('";', old_bootargs_start)
        new_bootargs = 'bootargs = "console=ttyMSM0,115200n8 earlycon=msm_serial_dm,0x078af000 maxcpus=1 nowatchdog panic=0 ubi.mtd=rootfs root=mtd:ubi_rootfs rootfstype=squashfs rootwait";'
        dts = dts[:old_bootargs_start] + new_bootargs + dts[old_bootargs_end+2:]

    # Injetar ramoops
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

    with open(temp_dts_win, "w", encoding="utf-8") as f:
        f.write(dts)

    run_wsl(f"cp '/mnt/h/FEITOS COM IA/Acer-Predator-Connect-T7/1 - Firmware e Imagens OpenWrt/temp_fdt618.dts' {WSL_WORK_DIR}/fdt-final.dts")
    ok, out = run_wsl(f"dtc -I dts -O dtb -o {WSL_WORK_DIR}/fdt-final.dtb {WSL_WORK_DIR}/fdt-final.dts 2>/dev/null")
    if not ok:
        print("[-] Falha ao compilar DTB com dtc.")
        return 1

    if os.path.exists(temp_dts_win):
        os.remove(temp_dts_win)

    # Criar ITS
    its_lines = [
        "/dts-v1/;",
        "/ {",
        '    description = "ARM64 Mainline Linux Kernel 6.18 for Acer Predator T7";',
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
        '            description = "Acer Predator Connect T7 Device Tree";',
        f'            data = /incbin/("{WSL_WORK_DIR}/fdt-final.dtb");',
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
        '            description = "OpenWrt Linux ARM64 with Ramoops";',
        '            kernel = "kernel-1";',
        '            fdt = "fdt-1";',
        "        };",
        "    };",
        "};"
    ]
    its_win_path = os.path.join(OUT_DIR, "temp_its.its")
    with open(its_win_path, "w", encoding="utf-8") as f:
        f.write("\n".join(its_lines))

    run_wsl(f"cp '/mnt/h/FEITOS COM IA/Acer-Predator-Connect-T7/1 - Firmware e Imagens OpenWrt/temp_its.its' {WSL_WORK_DIR}/final.its")
    if os.path.exists(its_win_path):
        os.remove(its_win_path)

    cmd_mk = f"cd {WSL_WORK_DIR} && mkimage -f final.its '{WSL_OUT_FIT}' > /dev/null"
    ok, out = run_wsl(cmd_mk)
    if not ok:
        print("[-] Falha no mkimage.")
        return 1

    run_wsl(f"rm -rf {WSL_WORK_DIR}")

    if os.path.exists(OUT_FIT):
        sz = os.path.getsize(OUT_FIT)
        print(f"[OK] Imagem final gerada: {OUT_FIT}")
        print(f"     Tamanho: {sz} bytes ({sz/(1024*1024):.2f} MB)")
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(main())
