import unittest

from shadowtools.validation import (
    ValidationError,
    normalize_domain,
    normalize_public_ip,
)


class ValidationTests(unittest.TestCase):
    def test_normalize_domain(self):
        self.assertEqual(normalize_domain("Example.COM."), "example.com")

    def test_reject_url(self):
        with self.assertRaises(ValidationError):
            normalize_domain("https://example.com/path")

    def test_reject_local_domain(self):
        with self.assertRaises(ValidationError):
            normalize_domain("printer.local")

    def test_public_ip(self):
        self.assertEqual(normalize_public_ip("1.1.1.1"), "1.1.1.1")

    def test_reject_private_ip(self):
        with self.assertRaises(ValidationError):
            normalize_public_ip("192.168.1.10")


if __name__ == "__main__":
    unittest.main()
