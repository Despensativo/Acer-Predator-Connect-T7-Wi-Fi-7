#!/usr/bin/env python3
"""Gera FITs .bin de seleção de slot sem alterar o ambiente U-Boot.

Construção offline. Não envia arquivos nem se conecta ao T7.
"""

from __future__ import annotations

import importlib.util
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = Path(__file__).resolve().parent
SOURCE = ROOT / "04_SCRIPTS_E_FERRAMENTAS/Teste_Selecao_Nativa_Slot2"
V1_HELPER = ROOT / "04_SCRIPTS_E_FERRAMENTAS/Alternador_Boot_T7/gerar_alternadores.py"
SOURCES = {
    1: ("bootconfig_slot1_original_RAW_NAO_WEB.bin", "bcb6b37e13b0231ce735f31705ecd97dde563a35c2605c0de467a77c35d56ebe"),
    2: ("bootconfig_slot2_nativo_RAW_NAO_WEB.bin", "e2f66a844a76c6e1bf5e80c855905a09b4ec259a9a5fa00fe628b87db59db163"),
}


def load_fit_helpers():
    spec = importlib.util.spec_from_file_location("t7_fit_v1_helpers", V1_HELPER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Gerador FIT V1 indisponível")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def script_for(slot: int) -> bytes:
    commands = [
        f"echo T7 V2: selecionando slot {slot} sem alterar APPSBLENV",
        "flashinit nand || exit 1",
        "imxtract $imgaddr bootconfig 0x45000000 || exit 1",
        "flash 0:BOOTCONFIG 0x45000000 0x80000 || exit 1",
        "nand device 0 || exit 1",
        "nand read 0x45100000 0x400000 0x80000 || exit 1",
        "cmp.b 0x45000000 0x45100000 0x80000 || exit 1",
        "flash 0:BOOTCONFIG1 0x45000000 0x80000 || exit 1",
        "nand read 0x45100000 0x480000 0x80000 || exit 1",
        "cmp.b 0x45000000 0x45100000 0x80000 || exit 1",
        f"echo T7 V2: BOOTCONFIG e BOOTCONFIG1 conferidos; reiniciando no slot {slot}",
        "reset",
    ]
    script = ("\n".join(commands) + "\n").encode("ascii")
    for forbidden in (b"fsbootargs", b"setenv", b"saveenv"):
        if forbidden in script:
            raise ValueError(f"Comando de ambiente inesperado: {forbidden!r}")
    return script


def main() -> None:
    helper = load_fit_helpers()
    configs = {}
    for slot, (name, expected) in SOURCES.items():
        data = (SOURCE / name).read_bytes()
        if len(data) != 0x80000 or helper.sha256(data) != expected:
            raise ValueError(f"Imagem de BOOTCONFIG inesperada: {name}")
        if data[:4] != bytes.fromhex("a0a1a2a3") or data[0x6C] != (1 if slot == 1 else 0):
            raise ValueError(f"Cabeçalho ou seletor inesperado: {name}")
        configs[slot] = data
    if [i for i, (a, b) in enumerate(zip(configs[1], configs[2])) if a != b] != [0x6C]:
        raise ValueError("Os BOOTCONFIG diferem além do byte seletor")

    padding = bytes(2 * 1024 * 1024)
    for slot in (1, 2):
        script = script_for(slot)
        with tempfile.TemporaryDirectory(prefix="t7-fit-v2-") as directory:
            temp = Path(directory)
            (temp / "script.txt").write_bytes(script)
            (temp / "bootconfig.bin").write_bytes(configs[slot])
            (temp / "padding.bin").write_bytes(padding)
            (temp / "selector.its").write_text(
                helper.fit_source(slot, script, configs[slot], padding), encoding="ascii"
            )
            result = subprocess.run(
                ["dtc", "-I", "dts", "-O", "dtb", "-o", "selector.itb", "selector.its"],
                cwd=temp, text=True, capture_output=True,
            )
            if result.returncode:
                raise RuntimeError(result.stderr)
            fit = (temp / "selector.itb").read_bytes()
            helper.inspect_fit(fit, script, configs[slot])
            output = OUTPUT / f"selecionar_slot{slot}_V2_CANDIDATO.bin"
            output.write_bytes(fit)
            (OUTPUT / f"script_slot{slot}_V2.txt").write_bytes(script)
            print(f"{output.name}: {len(fit)} bytes; SHA-256 {helper.sha256(fit)}")


if __name__ == "__main__":
    main()
