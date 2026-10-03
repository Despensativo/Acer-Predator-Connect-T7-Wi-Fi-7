"""Coletor futuro de identidade Linux e netconsole. Nao inicia sem --executar."""
import argparse
import ipaddress
import json
from pathlib import Path
import select
import socket
import time
import uuid
BASE = Path(__file__).resolve().parents[1]

def parse_identity(packet, expected):
    if len(packet) > 1200:
        raise ValueError("Datagrama excessivo")
    fields = packet.split(b"\t", 9)
    if len(fields) != 10:
        raise ValueError("Formato incompleto")
    magic, identity, boot, build, arch, kernel, interface, phase, sequence, body = fields
    if magic != b"T7NET1" or identity.decode("ascii") != expected["identity"]:
        raise ValueError("Identidade desconhecida")
    if build.decode("ascii") != expected["build"] or arch != b"aarch64":
        raise ValueError("Build/arquitetura divergente")
    kernel = kernel.decode("ascii")
    if not kernel.startswith("6.18.52-t7-net-20261002-v3"):
        raise ValueError("Kernel inesperado")
    boot = str(uuid.UUID(boot.decode("ascii")))
    if interface not in (b"lan", b"wan") or phase not in (b"INIT_REACHED", b"KMSG", b"HEARTBEAT"):
        raise ValueError("Interface/fase desconhecida")
    sequence = int(sequence)
    if not 0 < sequence <= 0xffffffff:
        raise ValueError("Sequencia invalida")
    return {"identity": expected["identity"], "boot_id": boot,
            "build": expected["build"], "arch": "aarch64", "kernel": kernel,
            "interface": interface.decode(), "phase": phase.decode(),
            "sequence": sequence, "body": body.decode("utf-8", "replace"),
            "init_reached_evidence": phase == b"INIT_REACHED"}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--identidade", type=Path, default=BASE/"identidade-net-v3.json")
    parser.add_argument("--executar", action="store_true")
    args = parser.parse_args()
    expected = json.loads(args.identidade.read_text(encoding="utf-8-sig"))
    if not args.executar:
        print("Coletor preparado. Nenhum socket aberto.")
        return
    if expected.get("hardware_ready") is not True:
        raise SystemExit("BLOQUEADO: sessao ainda nao validada para hardware")
    local = str(ipaddress.IPv4Address(expected["receiver_ip_candidate"]))
    # Confirma IP existente; nao configura interface ou firewall.
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as check:
        check.bind((local, 0))
    folder = BASE / "sessoes-rede" / uuid.uuid4().hex
    folder.mkdir(parents=True, exist_ok=False)
    allowed = set(expected["router_ips_candidates"])
    channels = []
    try:
        for port in (expected["udp_identity_port"], expected["udp_netconsole_port"]):
            channel = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Broadcast exige wildcard; remetentes e identidades sao filtrados.
            channel.bind(("0.0.0.0", port))
            channels.append(channel)
        print("Coletor iniciado. Ctrl+C encerra. Nenhum comando enviado ao roteador.")
        confirmed = set()
        deadline = time.monotonic() + 600
        while time.monotonic() < deadline:
            ready, _, _ = select.select(channels, [], [], 1)
            for channel in ready:
                data, peer = channel.recvfrom(65535)
                if peer[0] not in allowed:
                    continue
                event = {"pc_time_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                         "peer": peer, "port": channel.getsockname()[1]}
                if channel is channels[0]:
                    try:
                        event.update(parse_identity(data, expected))
                    except (ValueError, UnicodeError):
                        continue
                    if event["init_reached_evidence"] and event["boot_id"] not in confirmed:
                        confirmed.add(event["boot_id"])
                        print("INIT_REACHED confirmado para identidade esperada; arch=aarch64;",
                              "kernel="+event["kernel"], "boot_id="+event["boot_id"])
                else:
                    event.update({"kind": "netconsole_raw", "body": data.decode("utf-8","replace"),
                                  "init_reached_evidence": False})
                with (folder/"recebidos.jsonl").open("a",encoding="utf-8") as stream:
                    stream.write(json.dumps(event,ensure_ascii=False)+"\n")
    finally:
        for channel in channels: channel.close()

if __name__ == "__main__":
    main()
