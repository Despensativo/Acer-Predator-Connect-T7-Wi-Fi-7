"""Gera acionador somente com manifesto de sessao revisado; nao envia arquivos."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import uuid
import zlib
BASE = Path(__file__).resolve().parents[1]
manifest = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8-sig"))
required = ("runtime_ram_map", "dtb_fixups", "tftp_limits", "crc32_syntax",
            "http_dispatch", "autostart", "checkpoint_return")
if manifest.get("status") != "session_reviewed" or manifest.get("hardware_ready") is not True:
    raise SystemExit("BLOQUEADO: candidato nao aprovado para hardware")
if not all(manifest.get("validated", {}).get(key) is True for key in required):
    raise SystemExit("BLOQUEADO: faltam validacoes do U-Boot")
if manifest.get("mode", "load_and_verify") != "load_and_verify":
    raise SystemExit("Esta versao permite somente carregar e verificar; nao gera bootm")
session = uuid.UUID(hex=manifest["session_id"]).hex
fit = manifest["fit"]
path = (BASE / fit["path"]).resolve()
if not path.is_relative_to(BASE):
    raise SystemExit("FIT fora da pasta propria")
data = path.read_bytes()
crc = zlib.crc32(data) & 0xffffffff
if len(data) != fit["bytes"] or hashlib.sha256(data).hexdigest() != fit["sha256"]:
    raise SystemExit("FIT divergente")
address = int(fit["address"], 0)
record = int(manifest["checkpoint_address"], 0)
ranges = manifest["approved_ranges"]
def approved(start, end):
    return any(int(item["start"], 0) <= start and end <= int(item["end_exclusive"], 0)
               for item in ranges if item.get("approved") is True)
if not approved(address, address + len(data)) or not approved(record, record + 4096):
    raise SystemExit("Intervalos nao aprovados")
if address < record + 4096 and record < address + len(data):
    raise SystemExit("Intervalos se sobrepoem")
import ipaddress
server = str(ipaddress.IPv4Address(manifest["server_ip"]))
router = str(ipaddress.IPv4Address(manifest["router_ip"]))
name = fit["name"]
if not name or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_."
                   for c in name):
    raise SystemExit("Nome TFTP invalido")
scratch = record + 0x100
lines = ["echo T7_DIAG_LOAD_ONLY", f"setenv ipaddr {router}", f"setenv serverip {server}",
         "setenv autostart no", "setenv verify yes",
         f"mw.l 0x{record:x} 0 0x10", f"mw.l 0x{record:x} 0x37544744 1",
         f"mw.l 0x{record+4:x} 1 1", f"mw.l 0x{record+40:x} 0x{address:x} 1",
         f"mw.l 0x{record+44:x} 0x{len(data):x} 1",
         f"mw.l 0x{record+48:x} 0x{crc:x} 1"]
for index, byte in enumerate(bytes.fromhex(session)):
    lines.append(f"mw.b 0x{record+8+index:x} 0x{byte:x} 1")
def checkpoint(stage):
    return [f"mw.l 0x{record+24:x} 0x{stage:x} 1",
            f"if tftpput 0x{record:x} 0x40 {session}-{stage}.bin; then",
            "echo CHECKPOINT_OK", "else", "echo CHECKPOINT_FAILED", "exit 1", "fi"]
lines += checkpoint(0) + checkpoint(10)
lines += [f"if tftpboot 0x{address:x} {name}; then",
          f"if itest 0x${{filesize}} == 0x{len(data):x}; then",
          f"mw.l 0x{record+32:x} 0x{len(data):x} 1"]
lines += checkpoint(20)
lines += [f"if crc32 0x{address:x} 0x{len(data):x} 0x{scratch:x}; then",
          f"cp.l 0x{scratch:x} 0x{record+36:x} 1",
          f"if itest.l *0x{scratch:x} == 0x{crc:x}; then"]
lines += checkpoint(30)
lines += ["echo LOAD_VERIFIED_NO_BOOT", "exit 0",
          "else", "echo CRC_MISMATCH", "exit 1", "fi",
          "else", "echo CRC_FAILED", "exit 1", "fi",
          "else", "echo SIZE_MISMATCH", "exit 1", "fi",
          "else", "echo TFTP_FAILED", "exit 1", "fi"]
script = "\n".join(lines) + "\n"
# Defensive: generated commands are fixed; no network-provided command text.
destination = BASE / "artefatos" / ("launcher-" + session)
destination.mkdir(parents=True, exist_ok=False)
(destination / "script.txt").write_text(script, encoding="ascii", newline="\n")
its = '''/dts-v1/;
/ {
 description = "Flash RAM-only diagnostic launcher; load and verify";
 #address-cells = <1>;
 images { script {
  description = "No persistent writes and no boot";
  data = /incbin/("script.txt");
  type = "script"; arch = "arm"; os = "linux"; compression = "none";
  hash@1 { algo = "crc32"; };
 }; };
};
'''
(destination / "launcher.its").write_text(its, encoding="ascii", newline="\n")
subprocess.run(["mkimage", "-f", "launcher.its", "launcher.pending"],
               cwd=destination, check=True)
blob = (destination / "launcher.pending").read_bytes()
if blob[0x5c:0x60] != b"Flas":
    raise SystemExit("Marcador OEM divergente; arquivo bloqueado .pending")
minimum = manifest["validated_http_min_bytes"]
if not isinstance(minimum, int) or not 0 < minimum <= 65536:
    raise SystemExit("Limite HTTP nao valido")
blob += bytes(max(0, minimum - len(blob)))
if len(blob) > 65536:
    raise SystemExit("Acionador excede 64 KiB")
(destination / "launcher.itb").write_bytes(blob)
(destination / "manifesto-launcher.json").write_text(json.dumps({
    "mode": "load_and_verify", "includes_bootm": False,
    "bytes": len(blob), "sha256": hashlib.sha256(blob).hexdigest(),
    "script_sha256": hashlib.sha256(script.encode("ascii")).hexdigest(),
    "session": session, "uploaded": False}, indent=2) + "\n", encoding="utf-8")
print("Acionador gerado offline. Nenhum upload realizado.")
