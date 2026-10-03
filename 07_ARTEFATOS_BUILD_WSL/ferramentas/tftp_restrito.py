"""TFTP restrito para futura sessao autorizada. Nao inicia sem --executar.
Nenhum comando HTTP, upload, boot ou acesso remoto e executado por esta ferramenta.
"""
import argparse
import hashlib
import ipaddress
import json
from pathlib import Path
import socket
import struct
import time
import uuid
import zlib

BASE = Path(__file__).resolve().parents[1]
STAGES = {0, 10, 20, 30, 40, 255}

def decode_checkpoint(blob, session, stage, expected):
    if len(blob) != 64:
        raise ValueError("Registro deve ter exatamente 64 bytes")
    magic, version, sid, actual_stage, status, received, crc, address, size, expected_crc, reserved = struct.unpack(
        "<4sI16s7I12s", blob)
    if magic != b"DGT7" or version != 1 or sid != bytes.fromhex(session):
        raise ValueError("Identidade de protocolo/sessao divergente")
    if stage not in STAGES or actual_stage != stage or reserved != bytes(12):
        raise ValueError("Estagio ou preenchimento invalido")
    if status > 7:
        raise ValueError("Codigo de resultado desconhecido")
    if address != expected["address"] or size != expected["size"] or expected_crc != expected["crc32"]:
        raise ValueError("Registro nao corresponde ao artefato da sessao")
    if stage in {20, 30, 40} and (received != size or status != 0):
        raise ValueError("Etapa posterior exige tamanho correto e sucesso")
    if stage in {30, 40} and crc != expected_crc:
        raise ValueError("CRC divergente em etapa verificada")
    return {"stage": stage, "status": status, "received_bytes": received,
            "computed_crc32": format(crc, "08x"), "fit_address": hex(address),
            "linux_execution_proven": False}

def error(sock, peer, code, text):
    sock.sendto(struct.pack("!HH", 5, code) + text.encode("ascii", "replace")[:100] + b"\0", peer)

def read_request(packet):
    if len(packet) > 1024 or len(packet) < 6:
        raise ValueError("Pedido invalido")
    opcode = struct.unpack_from("!H", packet)[0]
    fields = packet[2:].split(b"\0")
    if opcode not in {1, 2} or len(fields) < 3 or fields[1].lower() != b"octet":
        raise ValueError("Somente RRQ/WRQ octet")
    name = fields[0].decode("ascii")
    if not name or any(char in name for char in ("/", "\\", "..")):
        raise ValueError("Nome invalido")
    # Opcoes TFTP adicionais nao sao negociadas: bloco padrao 512 bytes.
    return opcode, name

def transfer_read(sock, peer, blob):
    blocks = len(blob) // 512 + 1
    if blocks >= 65536:
        raise ValueError("Imagem excede limite de blocos")
    for block in range(1, blocks + 1):
        data = blob[(block - 1) * 512:block * 512]
        packet = struct.pack("!HH", 3, block) + data
        success = False
        for _ in range(5):
            sock.sendto(packet, peer)
            deadline = time.monotonic() + 2
            while time.monotonic() < deadline:
                try:
                    reply, sender = sock.recvfrom(2048)
                except socket.timeout:
                    break
                if sender == peer and reply == struct.pack("!HH", 4, block):
                    success = True
                    break
            if success:
                break
        if not success:
            raise TimeoutError("RRQ sem ACK")
    return {"completed": True, "bytes": len(blob)}

def receive_record(sock, peer):
    ack = struct.pack("!HH", 4, 0)
    for _ in range(5):
        sock.sendto(ack, peer)
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            try:
                packet, sender = sock.recvfrom(2048)
            except socket.timeout:
                break
            if sender != peer:
                continue
            if len(packet) != 68 or packet[:4] != struct.pack("!HH", 3, 1):
                raise ValueError("WRQ exige um unico bloco de exatamente 64 bytes")
            return packet[4:]
    raise TimeoutError("WRQ sem DATA")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifesto", type=Path, required=True)
    parser.add_argument("--executar", action="store_true", help="Inicia servidor; nao usar antes do aviso de teste")
    args = parser.parse_args()
    manifest = json.loads(args.manifesto.read_text(encoding="utf-8-sig"))
    if manifest.get("status") != "session_reviewed" or manifest.get("hardware_ready") is not True:
        raise SystemExit("Manifesto bloqueado: hardware_ready/status nao aprovados")
    session = manifest["session_id"]
    if len(session) != 32 or len(bytes.fromhex(session)) != 16:
        raise SystemExit("Sessao invalida")
    bind_ip = str(ipaddress.IPv4Address(manifest["server_ip"]))
    router_ip = str(ipaddress.IPv4Address(manifest["router_ip"]))
    if bind_ip == "0.0.0.0" or bind_ip == router_ip:
        raise SystemExit("Enderecos invalidos")
    fit = manifest["fit"]
    path = (BASE / fit["path"]).resolve()
    if not path.is_relative_to(BASE) or path.is_symlink():
        raise SystemExit("Imagem deve estar na pasta propria e nao ser link")
    blob = path.read_bytes()
    if len(blob) != fit["bytes"] or len(blob) > 16 * 1024 * 1024:
        raise SystemExit("Tamanho FIT divergente")
    if hashlib.sha256(blob).hexdigest() != fit["sha256"]:
        raise SystemExit("SHA256 FIT divergente")
    expected = {"address": int(fit["address"], 0), "size": len(blob),
                "crc32": zlib.crc32(blob) & 0xffffffff}
    if format(expected["crc32"], "08x") != fit["crc32"]:
        raise SystemExit("CRC manifesto divergente")
    if not args.executar:
        print("Manifesto conferido. Servidor NAO iniciado.")
        return
    logdir = BASE / "sessoes" / (session + "-" + uuid.uuid4().hex)
    logdir.mkdir(parents=True, exist_ok=False)
    names = {f"{session}-{stage}.bin": stage for stage in STAGES}
    seen = set()
    def event(value):
        value["pc_time_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with (logdir / "eventos.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(value, ensure_ascii=False) + "\n")
            stream.flush()
    print("Servidor iniciado na interface explicitamente definida; Ctrl+C encerra.")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as listener:
        listener.bind((bind_ip, 69))
        listener.settimeout(1)
        deadline = time.monotonic() + 600
        while time.monotonic() < deadline:
            try:
                packet, peer = listener.recvfrom(2048)
            except socket.timeout:
                continue
            if peer[0] != router_ip:
                error(listener, peer, 2, "Peer denied")
                continue
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as channel:
                channel.bind((bind_ip, 0))
                channel.settimeout(0.5)
                try:
                    opcode, name = read_request(packet)
                    event({"request": name, "opcode": opcode, "completed": False})
                    if opcode == 1 and name == fit["name"]:
                        result = transfer_read(channel, peer, blob)
                        event({"request": name, **result})
                    elif opcode == 2 and name in names:
                        record = receive_record(channel, peer)
                        stage = names[name]
                        parsed = decode_checkpoint(record, session, stage, expected)
                        required = {10: {0}, 20: {0, 10}, 30: {0, 10, 20},
                                    40: {0, 10, 20, 30}}.get(stage, set())
                        if not required.issubset(seen):
                            raise ValueError("Checkpoint fora de ordem")
                        with (logdir / (uuid.uuid4().hex + "-" + name)).open("xb") as stream:
                            stream.write(record)
                        event({"request": name, "completed": True, **parsed})
                        seen.add(stage)
                        final_ack = struct.pack("!HH", 4, 1)
                        channel.sendto(final_ack, peer)
                        # Responde retransmissoes do ultimo DATA por dois segundos.
                        linger = time.monotonic() + 2
                        while time.monotonic() < linger:
                            try:
                                duplicate, sender = channel.recvfrom(2048)
                            except socket.timeout:
                                continue
                            if sender == peer and duplicate == struct.pack("!HH", 3, 1) + record:
                                channel.sendto(final_ack, peer)
                    else:
                        error(channel, peer, 2, "Name denied; no fallback")
                except (ValueError, TimeoutError, OSError, UnicodeError) as exc:
                    event({"completed": False, "error": str(exc)})
                    error(channel, peer, 0, "Transfer rejected")
    event({"server_stopped": True, "linux_execution_proven": False})

if __name__ == "__main__":
    main()
