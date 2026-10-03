"""Gera FIT candidato offline. Nao cria acionador nem libera upload."""
import hashlib
import json
import lzma
from pathlib import Path
import struct
import subprocess
import sys
import zlib

out = Path(sys.argv[1]).resolve()
raw = (out / "Image").read_bytes()
if raw[56:60] != b"ARM\x64":
    raise SystemExit("Cabecalho ARM64 invalido")
offset, size, flags = struct.unpack_from("<QQQ", raw, 8)
if size == 0 or size > 32 * 1024 * 1024 or len(raw) > 32 * 1024 * 1024:
    raise SystemExit("Kernel excede o orcamento ou image_size indefinido")
load = 0x41000000
if (load - offset) % 0x200000:
    raise SystemExit("Alinhamento ARM64 invalido")
data = lzma.compress(raw, format=lzma.FORMAT_ALONE, preset=6)
data = data[:5] + struct.pack("<Q", len(raw)) + data[13:]
(out / "Image.lzma").write_bytes(data)
its = '''/dts-v1/;
/ {
    description = "T7 diagnostic candidate - NOT FOR HTTP FAILSAFE UPLOAD";
    #address-cells = <1>;
    images {
        kernel@1 {
            description = "New ARM64 kernel with minimal embedded initramfs";
            data = /incbin/("Image.lzma");
            type = "kernel"; arch = "arm64"; os = "linux";
            compression = "lzma";
            load = <0x41000000>; entry = <0x41000000>;
            hash@1 { algo = "crc32"; };
        };
        fdt@1 {
            description = "T7 conservative diagnostic DTB candidate";
            data = /incbin/("t7-diagnostico.dtb");
            type = "flat_dt"; arch = "arm64"; compression = "none";
            hash@1 { algo = "crc32"; };
        };
    };
    configurations {
        default = "config@mi01.6";
        config@mi01.6 { kernel = "kernel@1"; fdt = "fdt@1"; };
    };
};
'''
(out / "candidato.its").write_text(its, encoding="utf-8", newline="\n")
subprocess.run(["mkimage", "-f", "candidato.its", "t7-arm64-diag-CANDIDATO-NAO-ENVIAR.itb"],
               cwd=out, check=True)
fit = (out / "t7-arm64-diag-CANDIDATO-NAO-ENVIAR.itb").read_bytes()
if len(fit) > 16 * 1024 * 1024:
    raise SystemExit("FIT excede orcamento")
if lzma.decompress(data, format=lzma.FORMAT_ALONE) != raw:
    raise SystemExit("Verificacao LZMA falhou")
net_variant = "CONFIG_QCOM_PPE=y" in (out / "kernel.config").read_text()
manifest = {
    "status": "offline_build_candidate_not_hardware_ready",
    "hardware_ready": False, "upload_authorized": False,
    "boot_launcher_generated": False,
    "image_header": {"text_offset": hex(offset), "image_size": size, "flags": hex(flags)},
    "candidate_load": hex(load), "candidate_end": hex(load + size),
    "approved_addresses": None, "ramoops_region": None,
    "blockers": ["RAM dinamica U-Boot nao validada", "Fixups e posicao DTB nao validados",
                 "Retencao RAM e regiao ramoops nao validadas",
                 ("Ethernet e netconsole ainda nao testados; falhas anteriores ao driver sem retorno" if net_variant else "Saida Linux pela rede nao implementada; UART ainda necessaria"),
                 "Watchdog e transicao ARM64 precisam observacao no hardware"],
    "files": {}
}
for name in ("Image", "Image.lzma", "init", "t7-diagnostico.dtb", "kernel.config",
             "t7-arm64-diag-CANDIDATO-NAO-ENVIAR.itb"):
    blob = (out / name).read_bytes()
    manifest["files"][name] = {"bytes": len(blob),
        "sha256": hashlib.sha256(blob).hexdigest(),
        "crc32": format(zlib.crc32(blob) & 0xffffffff, "08x")}
(out / "manifesto-candidato.json").write_text(
    json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
(out / "NAO-ENVIAR-AO-ROTEADOR.md").write_text(
    "# Candidato sem aprovacao de hardware\n\n"
    "Nao enviar este FIT ao HTTP Failsafe: o handler pode tratar FIT comum como atualizacao e gravar flash.\n\n"
    "Este diretorio contem uma compilacao offline real. Nao ha acionador de upload aprovado. "
    "Enderecos, fixups do DTB, watchdog e observabilidade continuam pendentes. "
    "PSTORE/ramoops foram compilados, mas sem regiao exclusiva nao ha gravacao ramoops ativa.\n",
    encoding="utf-8")
