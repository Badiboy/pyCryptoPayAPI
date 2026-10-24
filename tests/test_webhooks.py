import hashlib
import hmac
import json
import unittest

from pyCryptoPayAPI import (
    CryptoPayWebhookParseError,
    CryptoPayWebhookSignatureError,
    Invoice,
    pyCryptoPayAPI,
    parse_and_verify_webhook,
    verify_webhook_signature,
)


TOKEN = "unit-test-token"
BODY = json.dumps({"update_id": 7, "update_type": "invoice_paid", "request_date": "2026-10-24T00:00:00Z", "payload": {"invoice_id": 1, "status": "paid"}}, separators=(",", ":")).encode()
SIGNATURE = hmac.new(hashlib.sha256(TOKEN.encode()).digest(), BODY, hashlib.sha256).hexdigest()


class WebhookTests(unittest.TestCase):
    def test_valid_invoice_paid_is_verified_and_parsed(self):
        update = parse_and_verify_webhook(BODY, SIGNATURE, TOKEN)
        self.assertEqual(7, update.update_id)
        self.assertIsInstance(update.payload, Invoice)

    def test_byte_mutation_fails_before_parsing(self):
        with self.assertRaises(CryptoPayWebhookSignatureError):
            parse_and_verify_webhook(BODY + b" ", SIGNATURE, TOKEN)

    def test_bad_signature_wins_over_invalid_json(self):
        with self.assertRaises(CryptoPayWebhookSignatureError):
            parse_and_verify_webhook(b"{", "bad", TOKEN)

    def test_valid_signature_with_invalid_json_is_parse_error(self):
        body = b"{"
        signature = hmac.new(hashlib.sha256(TOKEN.encode()).digest(), body, hashlib.sha256).hexdigest()
        with self.assertRaises(CryptoPayWebhookParseError):
            parse_and_verify_webhook(body, signature, TOKEN)

    def test_client_wrapper_uses_client_token(self):
        self.assertEqual(7, pyCryptoPayAPI(TOKEN, result_as_class=False).process_webhook(BODY, SIGNATURE).update_id)

    def test_verifier_rejects_non_bytes(self):
        with self.assertRaises(CryptoPayWebhookSignatureError):
            verify_webhook_signature({}, SIGNATURE, TOKEN)


if __name__ == "__main__":
    unittest.main()
