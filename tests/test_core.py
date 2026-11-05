import unittest

from core.ip_tools import inspect_ip
from core.security import normalize_domain


class CoreTests(unittest.TestCase):
    def test_domain_normalization(self):
        self.assertEqual(normalize_domain("Example.COM."), "example.com")

    def test_reject_url_as_domain(self):
        with self.assertRaises(ValueError):
            normalize_domain("https://example.com/path")

    def test_reject_local_domain(self):
        with self.assertRaises(ValueError):
            normalize_domain("printer.local")

    def test_ip_classification(self):
        result = inspect_ip("192.168.1.20")
        self.assertTrue(result["private"])
        self.assertFalse(result["global"])
        self.assertIsNone(result["reverse_dns"])

    def test_invalid_ip(self):
        with self.assertRaises(ValueError):
            inspect_ip("not-an-ip")


if __name__ == "__main__":
    unittest.main()
