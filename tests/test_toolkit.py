import gzip
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import audit
import render_blocklist as blocklist


class BlocklistTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / "data/indicators.json").read_text())

    def test_snapshot_is_consistent(self):
        domains, addresses = blocklist.validate(self.data)
        self.assertEqual(len(domains), 115)
        self.assertEqual(len(self.data["badbox2_c2_domains"]), 109)
        self.assertEqual(set(domains), set(self.data["badbox2_c2_domains"]) | set(self.data["related_jm_firmware_endpoints"]))
        self.assertEqual(len(addresses), 1)

    def test_dns_suffix_boundary(self):
        suffix = blocklist.wire_name("example.com")
        self.assertIn(suffix, blocklist.wire_name("example.com"))
        self.assertIn(suffix, blocklist.wire_name("a.example.com"))
        for control in ["notexample.com", "example.com.invalid", "example-company.com"]:
            self.assertNotIn(suffix, blocklist.wire_name(control))
        self.assertEqual(suffix, blocklist.wire_name("EXAMPLE.COM"))

    def test_invalid_domains_cannot_enter_rules(self):
        for value in ["x;reboot.com", "$(id).example", "x\n.example", "x..com", "-x.com", "x-.com", "á.com", "x.com ", "1.2.3.4", "x/evil.com", "a" * 64 + ".com"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                blocklist.normalize_domain(value)

    def test_duplicate_and_private_ip_rejected(self):
        with self.assertRaises(ValueError):
            blocklist.validate({"domains": ["a.com", "A.COM"]})
        with self.assertRaises(ValueError):
            blocklist.validate({"domains": ["a.com"], "blocked_ipv4": ["127.0.0.1"]})

    def test_generated_rules_only_flush_owned_chains(self):
        domains, addresses = blocklist.validate(self.data)
        for family in (4, 6):
            text = blocklist.render_rules(domains, addresses, family)
            flushes = [line for line in text.splitlines() if line.startswith("-F")]
            self.assertEqual(flushes, [f"-F HY320_BB{family}", f"-F HY320_DNS{family}"])
            self.assertEqual(text.count("--hex-string"), 115)
            self.assertEqual(text.count("--icase"), 115)
            self.assertNotIn("-A OUTPUT", text)
            self.assertTrue(text.endswith("COMMIT\n"))


class AuditTests(unittest.TestCase):
    def test_config_selection_drops_unrelated_values(self):
        config = '# CONFIG_SECURITY_SELINUX is not set\nCONFIG_SECURITY=y\nCONFIG_LOCALVERSION="private value"\n'
        self.assertEqual(audit.parse_config(config), {"CONFIG_SECURITY_SELINUX": "n", "CONFIG_SECURITY": "y"})

    def test_unexpected_and_private_scalars_are_discarded(self):
        for value in ["owner@example.com", "192.0.2.10", "AA:BB:CC:DD:EE:FF", "1\nextra", "-----BEGIN PRIVATE KEY-----"]:
            self.assertIsNone(audit.safe_scalar("device_variant", value))
        self.assertIsNone(audit.safe_scalar("adb_transport_guard", "anything"))

    def test_collection_is_read_only_and_does_not_emit_device_selector(self):
        calls = []
        config = gzip.compress(b'# CONFIG_SECURITY_SELINUX is not set\nCONFIG_SECURITY=y\n')

        def run(command):
            calls.append(command)
            if command[0] == "exec-out":
                return 0, config
            if command[1] == "getprop ro.product.device":
                return 0, b"t950s_be311\n"
            if command[1] == "getprop sys.hy320.adb_transport":
                return 0, b"tls\n"
            return 0, b"1\n"

        report = audit.collect(run)
        self.assertFalse(report["selinux_compiled_in"])
        self.assertTrue(report["matches_documented_variant"])
        for command in calls:
            self.assertTrue(command == ["exec-out", "head", "-c", "524288", "/proc/config.gz"] or command == ["shell", next(value for value in audit.PROPERTIES.values() if value == command[1])])
        text = json.dumps(report)
        self.assertNotIn("serial", text)
        self.assertNotIn("adbkey", text)

    def test_absent_or_invalid_kernel_config_is_unknown(self):
        for result in [(1, b""), (0, b"invalid gzip")]:
            report = audit.collect(lambda command: result if command[0] == "exec-out" else (1, b""))
            self.assertIsNone(report["selinux_compiled_in"])


if __name__ == "__main__":
    unittest.main()
