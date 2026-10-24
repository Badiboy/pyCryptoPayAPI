"""Manually run live Crypto Pay error-response regression checks.

This module is intentionally not named ``test_*.py`` so standard unittest
discovery never imports it. Launch it explicitly with
``RUN_CRYPTO_PAY_LIVE_ERROR_TESTS=1``.
"""

import os
import sys
import unittest
import json
from pathlib import Path


LIVE_TEST_FLAG = "RUN_CRYPTO_PAY_LIVE_ERROR_TESTS"
PACKAGE_ROOT = Path(__file__).resolve().parents[1]

if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))


def require_live_test_flag():
    """Reject an accidental manual run before loading any credential."""
    if os.environ.get(LIVE_TEST_FLAG) != "1":
        raise RuntimeError(
            "Refusing live Crypto Pay API calls. "
            "Set RUN_CRYPTO_PAY_LIVE_ERROR_TESTS=1 to run this module."
        )


class LiveErrorResponseTests(unittest.TestCase):
    """Compare each real failed API envelope with SDK exception fields."""

    @classmethod
    def setUpClass(cls):
        require_live_test_flag()
        from pyCryptoPayAPI import pyCryptoPayAPI
        from pyCryptoPayAPI.test_config import load_test_api_token

        cls.client = pyCryptoPayAPI(
            load_test_api_token(), result_as_class=False, print_errors=False
        )
        cls.invalid_token_client = pyCryptoPayAPI(
            "000000:invalid-token", result_as_class=False, print_errors=False
        )

    def assert_real_api_error(self, expected_status_code, expected_method, call):
        from pyCryptoPayAPI import MAIN_API_URL, pyCryptoPayException

        with self.assertRaises(pyCryptoPayException) as caught:
            call()

        error = caught.exception
        self.assertIsNone(error.cause)
        self.assertEqual(expected_status_code, error.status_code)
        self.assertEqual(MAIN_API_URL + expected_method, error.request_url)
        self.assertIsInstance(error.response_text, str)

        response = json.loads(error.response_text)
        self.assertIs(False, response.get("ok"))
        api_error = response.get("error")
        self.assertIsInstance(api_error, dict)

        self.assertEqual(api_error.get("code", 1), error.code)
        self.assertEqual(api_error.get("name", "---"), error.name)
        self.assertEqual(
            api_error.get("message", api_error.get("description", "No info")),
            error.message,
        )
        self.assertEqual(str(api_error), error.full_error)
        return api_error

    def test_invalid_token_keeps_unauthorized_response(self):
        api_error = self.assert_real_api_error(
            401, "getMe", self.invalid_token_client.get_me
        )
        self.assertEqual("UNAUTHORIZED", api_error.get("name"))
        self.assertNotIn("message", api_error)
        self.assertNotIn("description", api_error)

    def test_invalid_invoice_status_keeps_allowed_statuses(self):
        api_error = self.assert_real_api_error(
            400,
            "getInvoices",
            lambda: self.client.get_invoices(status="not-a-status"),
        )
        self.assertEqual("STATUS_INVALID", api_error.get("name"))
        self.assertEqual(["active", "paid"], api_error.get("allowed_statuses"))

    def test_unsupported_invoice_asset_keeps_allowed_assets(self):
        api_error = self.assert_real_api_error(
            400,
            "createInvoice",
            lambda: self.client.create_invoice(asset="NOT_A_CURRENCY", amount="1"),
        )
        self.assertEqual("UNSUPPORTED_ASSET", api_error.get("name"))
        self.assertIsInstance(api_error.get("allowed_crypto_assets"), list)
        self.assertIn("TON", api_error["allowed_crypto_assets"])

    def test_missing_paid_button_url_keeps_required_field_error(self):
        api_error = self.assert_real_api_error(
            400,
            "createInvoice",
            lambda: self.client.create_invoice(
                asset="TON", amount="1", paid_btn_name="viewItem"
            ),
        )
        self.assertEqual("PAID_BTN_URL_REQUIRED", api_error.get("name"))

    def test_disabled_transfer_uses_description_as_message(self):
        api_error = self.assert_real_api_error(
            403,
            "transfer",
            lambda: self.client._pyCryptoPayAPI__request("transfer"),
        )
        self.assertEqual("METHOD_DISABLED", api_error.get("name"))
        self.assertIsInstance(api_error.get("description"), str)


if __name__ == "__main__":
    try:
        require_live_test_flag()
    except RuntimeError as error:
        print(error, file=sys.stderr)
        raise SystemExit(2)
    unittest.main()
