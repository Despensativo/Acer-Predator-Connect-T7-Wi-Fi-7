"""Verificacoes locais com sockets simulados; nao abre rede nem acessa roteador."""
import importlib.util
from pathlib import Path
import socket
import struct
import unittest

location = Path(__file__).with_name("tftp_restrito.py")
spec = importlib.util.spec_from_file_location("tftp_diag", location)
tftp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tftp)
SID = "00112233445566778899aabbccddeeff"
EXPECTED = {"address": 0x46000000, "size": 1024, "crc32": 0x12345678}

def record(stage=30, size=1024, crc=0x12345678):
    return struct.pack("<4sI16s7I12s", b"DGT7", 1, bytes.fromhex(SID),
                       stage, 0, size, crc, EXPECTED["address"], EXPECTED["size"],
                       EXPECTED["crc32"], bytes(12))

class Channel:
    def __init__(self, replies):
        self.replies = list(replies)
        self.sent = []
    def sendto(self, packet, peer):
        self.sent.append((packet, peer))
    def recvfrom(self, count):
        item = self.replies.pop(0)
        if item is None:
            raise socket.timeout()
        return item

class ProtocolTests(unittest.TestCase):
    def test_valid_checkpoint_does_not_prove_linux(self):
        value = tftp.decode_checkpoint(record(), SID, 30, EXPECTED)
        self.assertFalse(value["linux_execution_proven"])
    def test_reject_bad_crc_and_size(self):
        for blob in (record(crc=0), record(size=1), record()[:-1]):
            with self.assertRaises(ValueError):
                tftp.decode_checkpoint(blob, SID, 30, EXPECTED)
    def test_reject_foreign_session(self):
        with self.assertRaises(ValueError):
            tftp.decode_checkpoint(record(), "ff" * 16, 30, EXPECTED)
    def test_reject_reserved_bytes(self):
        blob = record()[:-1] + b"x"
        with self.assertRaises(ValueError):
            tftp.decode_checkpoint(blob, SID, 30, EXPECTED)
    def test_path_and_mode_rejected(self):
        for request in (b"\0\1../other\0octet\0", b"\0\1name\0netascii\0"):
            with self.assertRaises(ValueError):
                tftp.read_request(request)
    def test_rrq_retries_lost_ack(self):
        peer = ("192.0.2.1", 1234)
        channel = Channel([None, (struct.pack("!HH", 4, 1), peer)])
        result = tftp.transfer_read(channel, peer, b"data")
        self.assertTrue(result["completed"])
        self.assertEqual(len(channel.sent), 2)
        self.assertEqual(channel.sent[0], channel.sent[1])
    def test_rrq_exact_block_has_empty_final_block(self):
        peer = ("192.0.2.1", 1234)
        channel = Channel([(struct.pack("!HH", 4, 1), peer),
                           (struct.pack("!HH", 4, 2), peer)])
        tftp.transfer_read(channel, peer, bytes(512))
        self.assertEqual(channel.sent[1][0], struct.pack("!HH", 3, 2))
    def test_wrq_rejects_oversized_record(self):
        peer = ("192.0.2.1", 1234)
        channel = Channel([(struct.pack("!HH", 3, 1) + bytes(65), peer)])
        with self.assertRaises(ValueError):
            tftp.receive_record(channel, peer)

if __name__ == "__main__":
    unittest.main(verbosity=2)
