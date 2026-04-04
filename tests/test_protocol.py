"""Tests unitarios para shared/protocol.py"""
import struct
import unittest
from shared.protocol import create_message, create_response, encode, decode


class TestProtocol(unittest.TestCase):

    def test_create_message_has_required_fields(self):
        msg = create_message("lock_screen")
        self.assertEqual(msg["type"], "command")
        self.assertEqual(msg["action"], "lock_screen")
        self.assertIn("timestamp", msg)
        self.assertIn("request_id", msg)
        self.assertIsInstance(msg["payload"], dict)

    def test_create_message_with_payload(self):
        msg = create_message("test", payload={"key": "value"})
        self.assertEqual(msg["payload"], {"key": "value"})

    def test_create_response_has_required_fields(self):
        resp = create_response("abc-123", "ok", "done")
        self.assertEqual(resp["type"], "response")
        self.assertEqual(resp["request_id"], "abc-123")
        self.assertEqual(resp["status"], "ok")
        self.assertEqual(resp["message"], "done")

    def test_encode_decode_roundtrip(self):
        original = {"type": "command", "action": "ping", "payload": {}}
        encoded = encode(original)
        length = struct.unpack("!I", encoded[:4])[0]
        decoded = decode(encoded[4:])
        self.assertEqual(decoded, original)
        self.assertEqual(length, len(encoded) - 4)

    def test_encode_has_4_byte_prefix(self):
        msg = encode({"a": 1})
        self.assertGreater(len(msg), 4)
        length = struct.unpack("!I", msg[:4])[0]
        self.assertEqual(length, len(msg) - 4)


if __name__ == "__main__":
    unittest.main()
