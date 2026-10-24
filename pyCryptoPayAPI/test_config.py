"""Local-only configuration helpers for live API tests."""

import os
from pathlib import Path


TOKEN_ENVIRONMENT_VARIABLE = "CRYPTO_PAY_TEST_API_TOKEN"


def load_test_api_token(environment=None, env_file=None):
    """Return the test token from the environment or a local ignored .env file."""
    environment = os.environ if environment is None else environment
    token = environment.get(TOKEN_ENVIRONMENT_VARIABLE)
    if token:
        return token.strip()

    env_file = Path(env_file) if env_file is not None else Path(__file__).parent.parent / ".env"
    if env_file.is_file():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            name, separator, value = line.partition("=")
            if name.strip() == TOKEN_ENVIRONMENT_VARIABLE and separator and value.strip():
                return value.strip()

    raise RuntimeError(
        f"Set {TOKEN_ENVIRONMENT_VARIABLE} or add it to the local .env file before live API tests."
    )
