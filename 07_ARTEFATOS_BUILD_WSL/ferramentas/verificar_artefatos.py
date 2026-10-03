"""Verificacao offline independente do FIT, Image, initramfs e configuracao."""
import hashlib
import json
import lzma
from pathlib import Path
import struct
import sys
import zlib
BASE = Path(__file__).resolve().parents[1]

def fdt(blob):
    if len(blob) < 40:
        raise ValueError("FDT curto")
    magic, total, off, strings, reserve, version, compatible, cpu, sstrings, ssize = struct.unpack_from(">10I", blob)
    if magic != 0xd00dfeed or total > len(blob) or off + ssize > total or strings + sstrings > total:
        raise ValueError("FDT com limites invalidos")
    names = blob[strings:strings+sstrings]
    stack, nodes = [], {}
    end = off + ssize
    while off < end:
        token = struct.unpack_from(">I", blob, off)[0]; off += 4
        if token == 1:
            terminator = blob.index(0, off, end)
            name = blob[off:terminator].decode("ascii")
            off = (terminator + 4) & ~3
            stack.append(name)
            nodes["/" + "/".join(stack[1:])] = {}
        elif token == 2:
            if not stack: raise ValueError("FDT stack")
            stack.pop()
        elif token == 3:
            size, nameoff = struct.unpack_from(">II", blob, off); off += 8
            if off + size > end or nameoff >= len(names): raise ValueError("FDT propriedade")
            name = names[nameoff:names.index(0, nameoff)].decode("ascii")
            nodes["/" + "/".join(stack[1:])][name] = blob[off:off+size]
            off = (off + size + 3) & ~3
        elif token == 4:
            pass
        elif token == 9:
            return nodes
        else:
            raise ValueError("FDT token")
    raise ValueError("FDT sem terminador")

def cpio_entries(blob):
    result = {}; offset = 0
    while offset + 110 <= len(blob):
        header = blob[offset:offset+110]; offset += 110
        if header[:6] != b"070701": raise ValueError("CPIO nao newc")
        fields = [int(header[6+i*8:14+i*8],16) for i in range(13)]
        length, namesize = fields[6], fields[11]
        name = blob[offset:offset+namesize].rstrip(b"\0").decode("ascii")
        offset = (offset + namesize + 3) & ~3
        data = blob[offset:offset+length]
        if len(data) != length: raise ValueError("CPIO curto")
        offset = (offset + length + 3) & ~3
        if name == "TRAILER!!!": return result
        if name in result: raise ValueError("CPIO duplicado")
        result[name] = {"mode": fields[1], "bytes": length, "data": data}
    raise ValueError("CPIO sem trailer")

def main():
    out = Path(sys.argv[1]).resolve()
    archive = Path(sys.argv[2]).read_bytes()
    if not out.is_relative_to(BASE): raise SystemExit("Saida fora da pasta propria")
    fitbytes = (out / "t7-arm64-diag-CANDIDATO-NAO-ENVIAR.itb").read_bytes()
    fit = fdt(fitbytes)
    compressed = fit["/images/kernel@1"]["data"]
    raw = lzma.decompress(compressed, format=lzma.FORMAT_ALONE)
    assert raw == (out / "Image").read_bytes()
    assert raw[56:60] == b"ARMd"
    offset, imagesize = struct.unpack_from("<QQ", raw, 8)
    assert 0 < imagesize <= 32*1024*1024
    assert 0x41000000 + imagesize <= 0x43000000
    assert (0x41000000 - offset) % 0x200000 == 0
    assert fit["/images/kernel@1"]["compression"] == b"lzma\0"
    assert fit["/images/kernel@1"]["arch"] == b"arm64\0"
    assert fit["/configurations"]["default"] == b"config@mi01.6\0"
    assert fit["/configurations/config@mi01.6"]["kernel"] == b"kernel@1\0"
    assert fit["/configurations/config@mi01.6"]["fdt"] == b"fdt@1\0"
    for image in ("kernel@1", "fdt@1"):
        assert fit["/images/"+image+"/hash@1"]["algo"] == b"crc32\0"
        expected_crc = struct.unpack(">I", fit["/images/"+image+"/hash@1"]["value"])[0]
        assert expected_crc == (zlib.crc32(fit["/images/"+image]["data"]) & 0xffffffff)
    dtb = fit["/images/fdt@1"]["data"]
    assert dtb == (out / "t7-diagnostico.dtb").read_bytes()
    nodes = fdt(dtb)
    assert struct.unpack(">4I", nodes["/memory@40000000"]["reg"]) == (0, 0x40000000, 0, 0x20000000)
    bootargs = nodes["/chosen"]["bootargs"].rstrip(b"\0").decode()
    assert "ubi.mtd" not in bootargs and "root=mtd" not in bootargs
    assert "earlycon=msm_serial_dm,0x78af000" in bootargs
    assert not any(b"ramoops" in props.get("compatible", b"") for props in nodes.values())
    entries = cpio_entries(archive)
    assert set(entries) == {"dev", "proc", "sys", "tmp", "init", "dev/console"}
    assert entries["init"]["data"] == (out / "init").read_bytes()
    elf = entries["init"]["data"]
    assert elf[:5] == b"\x7fELF\x02" and struct.unpack_from("<H", elf,18)[0] == 183
    phoff = struct.unpack_from("<Q", elf,32)[0]
    phsize, phcount = struct.unpack_from("<HH", elf,54)
    assert all(struct.unpack_from("<I",elf,phoff+i*phsize)[0] != 3 for i in range(phcount))
    config = {}
    for line in (out / "kernel.config").read_text().splitlines():
        if line.startswith("CONFIG_") and "=" in line:
            k,v = line.split("=",1); config[k] = v
        elif line.startswith("# CONFIG_") and line.endswith(" is not set"):
            config[line[2:-11]] = "n"
    for symbol in ("ARM64", "PSTORE", "PSTORE_RAM", "PSTORE_CONSOLE", "DEVTMPFS",
                   "SERIAL_MSM_CONSOLE", "QCOM_SCM", "IPQ_GCC_5332", "CMDLINE_FORCE"):
        assert config["CONFIG_"+symbol] == "y", symbol
    for symbol in ("MTD", "MODULES", "DEVMEM", "NVMEM_SYSFS", "NVMEM_QCOM_QFPROM",
                   "MMC", "SCSI", "PCI", "USB", "NETDEVICES"):
        assert config.get("CONFIG_"+symbol, "n") == "n", symbol
    symbols = (out / "simbolos-diagnostico.txt").read_text()
    assert "ramoops_probe" in symbols and "pstore_register" in symbols
    report = {
        "offline_checks_passed": True, "hardware_ready": False, "upload_authorized": False,
        "fit_bytes": len(fitbytes), "image_bytes": len(raw),
        "arm64_image_size": imagesize, "candidate_end": hex(0x41000000+imagesize),
        "init_static_arm64": True, "initramfs_entries": [
            {"name": key, "bytes": value["bytes"], "mode": oct(value["mode"])}
            for key,value in entries.items()],
        "ramoops_compiled": True, "ramoops_region_configured": False,
        "flash_mtd_disabled": True, "fuse_qfprom_provider_disabled": True,
        "linux_physical_network_drivers_disabled": True,
        "missing_child_config_explanation": {
            "CONFIG_USB_STORAGE": "Kconfig depende de SCSI; SCSI=n e USB=n",
            "CONFIG_BLK_DEV_NVME": "Kconfig depende de PCI; PCI=n"},
        "fit_sha256": hashlib.sha256(fitbytes).hexdigest(),
        "initramfs_sha256": hashlib.sha256(archive).hexdigest(),
        "limitations": ["Nao comprova funcionamento em hardware", "Mapa dinamico e fixups desconhecidos",
                       "Sem UART ou outra saida validada, logs Linux permanecem sem retorno",
                       "Watchdog depende de probe e nao garante sobreviver ate o driver iniciar"]}
    with (out / "verificacao-offline.json").open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(report, ensure_ascii=False, indent=2)+"\n")
    print(json.dumps({key: report[key] for key in (
        "offline_checks_passed", "hardware_ready", "fit_bytes", "image_bytes", "candidate_end")}))
if __name__ == "__main__":
    main()
