"""Teste de parser em memoria; nao abre sockets."""
import importlib.util
from pathlib import Path
import unittest
location = Path(__file__).with_name("coletar_rede_v3.py")
spec = importlib.util.spec_from_file_location("collector",location)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
EXPECTED = {"identity":"00112233445566778899aabbccddeeff","build":"t7-net-20261002-v3"}
BASE = b"T7NET1\t00112233445566778899aabbccddeeff\t11111111-2222-3333-4444-555555555555\tt7-net-20261002-v3\taarch64\t6.18.52-t7-net-20261002-v3\tlan\tINIT_REACHED\t1\tAlive"
class IdentityTests(unittest.TestCase):
    def test_expected_init(self):
        self.assertTrue(module.parse_identity(BASE,EXPECTED)["init_reached_evidence"])
    def test_logs_are_not_init(self):
        value=BASE.replace(b"INIT_REACHED",b"KMSG")
        self.assertFalse(module.parse_identity(value,EXPECTED)["init_reached_evidence"])
    def test_reject_wrong_identity(self):
        with self.assertRaises(ValueError):
            module.parse_identity(BASE.replace(b"00112233",b"ffffffff"),EXPECTED)
    def test_reject_wrong_arch_and_unknown_boot(self):
        for value in (BASE.replace(b"aarch64",b"armv7l"),
                      BASE.replace(b"11111111-2222-3333-4444-555555555555",b"unknown")):
            with self.assertRaises(ValueError): module.parse_identity(value,EXPECTED)
if __name__=="__main__":
    unittest.main(verbosity=2)
