"""Auditoria offline: le configuracao e especificacao; nunca acessa o roteador."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parent

def read_config(path):
    result = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("CONFIG_") and "=" in line:
            name, value = line.split("=", 1)
            result[name] = value
        elif line.startswith("# CONFIG_") and line.endswith(" is not set"):
            result[line[2:-11]] = "n"
    return result

def audit(config_path, spec_path):
    config = read_config(config_path)
    spec = json.loads(spec_path.read_text(encoding="utf-8-sig"))
    checks = []
    requirements = spec["kernel_requirements"]
    for group, expected in (("must_be_y", "y"), ("must_be_n", "n")):
        for name in requirements[group]:
            actual = config.get(name)
            # Ausencia nao comprova desativacao: pode ser simbolo incorreto.
            checks.append({"symbol": name, "expected": expected,
                           "observed": actual, "pass": actual == expected})
    source = config.get("CONFIG_INITRAMFS_SOURCE")
    return {
        "scope": "offline_configuration_only",
        "config_path": str(config_path),
        "config_sha256": hashlib.sha256(config_path.read_bytes()).hexdigest(),
        "spec_sha256": hashlib.sha256(spec_path.read_bytes()).hexdigest(),
        "checks": checks,
        "failed_count": sum(not item["pass"] for item in checks),
        "initramfs_source": source,
        "initramfs_content_verified": False,
        "hardware_ready": False,
        "upload_authorized": False,
        "limitations": [
            "Nao examina o binario final nem prova ausencia de acesso a flash.",
            "Ausencia de simbolo exige verificar o Kconfig; nao equivale a n.",
            "Nao valida DTB, memoria, watchdog, FIT, U-Boot ou initramfs.",
            "Mesmo com todas as verificacoes aprovadas, hardware_ready permanece false."
        ]
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--spec", type=Path, default=BASE / "Relatorios anteriores" /
                        "ESPECIFICACAO-DIAGNOSTICO-RAM-2026-10-02.json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.output:
        target = args.output.resolve()
        if not target.is_relative_to(BASE):
            parser.error("O resultado deve ficar dentro de Feito por ChatGPT.")
        if target.exists():
            parser.error("O destino ja existe; use outro nome para preservar historico.")
    report = audit(args.config, args.spec)
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        with args.output.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
    print("Requisitos divergentes ou nao confirmados:", report["failed_count"])
    for item in report["checks"]:
        if not item["pass"]:
            print(item["symbol"], "esperado=" + item["expected"],
                  "observado=" + str(item["observed"]))
    print("Imagem liberada para hardware: NAO")
    return 1 if report["failed_count"] else 0

if __name__ == "__main__":
    sys.exit(main())
