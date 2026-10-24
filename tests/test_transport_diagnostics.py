import unittest
from unittest.mock import MagicMock, Mock, patch

import requests

from pyCryptoPayAPI import pyCryptoPayAPI, pyCryptoPayException


class TransportDiagnosticsTests(unittest.TestCase):
    def test_default_timeout_is_ten_seconds(self):
        self.assertEqual(10, pyCryptoPayAPI("token", result_as_class=False).timeout)

    def test_explicit_timeout_is_preserved(self):
        self.assertIsNone(pyCryptoPayAPI("token", result_as_class=False, timeout=None).timeout)

    def test_timeout_is_forwarded_to_requests_get(self):
        for configured_timeout in (10, 3.5, None):
            with self.subTest(timeout=configured_timeout):
                client = pyCryptoPayAPI(
                    "token", result_as_class=False, timeout=configured_timeout
                )
                response = Mock()
                response.json.return_value = {"ok": True, "result": {}}

                with patch("pyCryptoPayAPI.api.requests.get", return_value=response) as get:
                    client.get_me()

                self.assertEqual(configured_timeout, get.call_args.kwargs["timeout"])

    def test_transport_error_exposes_url_and_cause(self):
        client = pyCryptoPayAPI("token", result_as_class=False)

        with patch(
            "pyCryptoPayAPI.api.requests.get",
            side_effect=requests.ConnectionError("offline"),
        ):
            with self.assertRaises(pyCryptoPayException) as caught:
                client.get_me()

        self.assertEqual("TRANSPORT", caught.exception.name)
        self.assertEqual("https://pay.crypt.bot/api/getMe", caught.exception.request_url)
        self.assertIsInstance(caught.exception.cause, requests.ConnectionError)

    def test_non_json_response_exposes_status_and_body(self):
        client = pyCryptoPayAPI("token", result_as_class=False)
        response = MagicMock(status_code=502, text="gateway failure", url="https://pay.crypt.bot/api/getMe")
        response.__bool__.return_value = False
        response.json.side_effect = ValueError("invalid JSON")

        with patch("pyCryptoPayAPI.api.requests.get", return_value=response):
            with self.assertRaises(pyCryptoPayException) as caught:
                client.get_me()

        self.assertEqual("JSON", caught.exception.name)
        self.assertEqual(502, caught.exception.status_code)
        self.assertEqual("gateway failure", caught.exception.response_text)
        self.assertEqual("https://pay.crypt.bot/api/getMe", caught.exception.request_url)

    def test_api_error_preserves_http_diagnostics(self):
        client = pyCryptoPayAPI("token", result_as_class=False)
        response = Mock(status_code=400, text='{"ok": false}', url="https://pay.crypt.bot/api/getMe")
        response.json.return_value = {
            "ok": False,
            "error": {"code": 4001, "name": "TOKEN_INVALID", "message": "Token invalid"},
        }

        with patch("pyCryptoPayAPI.api.requests.get", return_value=response):
            with self.assertRaises(pyCryptoPayException) as caught:
                client.get_me()

        self.assertEqual(4001, caught.exception.code)
        self.assertEqual("TOKEN_INVALID", caught.exception.name)
        self.assertEqual(400, caught.exception.status_code)
        self.assertEqual('{"ok": false}', caught.exception.response_text)


if __name__ == "__main__":
    unittest.main()
