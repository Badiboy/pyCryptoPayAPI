import os
import tempfile
import unittest
from pathlib import Path
import subprocess
import sys

from pyCryptoPayAPI.test_config import load_test_api_token


class LoadTestApiTokenTests(unittest.TestCase):
    def test_live_api_module_is_skipped_without_explicit_flag(self):
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "pyCryptoPayAPI/tests.py"],
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("skipped", result.stdout.lower())

    def test_environment_value_has_priority_over_env_file(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            env_file = Path(temporary_directory) / ".env"
            env_file.write_text("CRYPTO_PAY_TEST_API_TOKEN=file-token\n", encoding="utf-8")

            token = load_test_api_token(
                environment={"CRYPTO_PAY_TEST_API_TOKEN": "environment-token"},
                env_file=env_file,
            )

        self.assertEqual("environment-token", token)

    def test_env_file_supplies_token_when_environment_is_empty(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            env_file = Path(temporary_directory) / ".env"
            env_file.write_text("CRYPTO_PAY_TEST_API_TOKEN=file-token\n", encoding="utf-8")

            token = load_test_api_token(environment={}, env_file=env_file)

        self.assertEqual("file-token", token)

    def test_missing_token_raises_clear_error(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            env_file = Path(temporary_directory) / ".env"

            with self.assertRaisesRegex(RuntimeError, "CRYPTO_PAY_TEST_API_TOKEN"):
                load_test_api_token(environment={}, env_file=env_file)


if __name__ == "__main__":
    unittest.main()
