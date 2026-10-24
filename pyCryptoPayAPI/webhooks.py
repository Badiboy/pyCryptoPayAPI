"""Framework-independent Crypto Pay webhook verification and parsing."""

import hashlib
import hmac
import json

from .classes import Invoice, Update


class CryptoPayWebhookError(ValueError):
    """Base error for invalid inbound Crypto Pay webhook data."""


class CryptoPayWebhookSignatureError(CryptoPayWebhookError):
    """Raised when the signature is absent, malformed, or does not match."""


class CryptoPayWebhookParseError(CryptoPayWebhookError):
    """Raised when a verified raw body cannot be decoded as a webhook update."""


def verify_webhook_signature(raw_body, signature, token):
    """Verify a Crypto Pay signature over exact raw HTTP request bytes.

    The caller must obtain ``raw_body`` before JSON parsing and pass the
    ``crypto-pay-api-signature`` header value. HTTP reception, replay policy,
    database-backed idempotency, and business effects remain application-owned.
    """
    if not isinstance(raw_body, bytes):
        raise CryptoPayWebhookSignatureError("raw_body must be bytes")
    if not isinstance(signature, str) or not signature:
        raise CryptoPayWebhookSignatureError("signature must be a non-empty string")
    if not isinstance(token, str) or not token:
        raise CryptoPayWebhookSignatureError("token must be a non-empty string")
    key = hashlib.sha256(token.encode("utf-8")).digest()
    expected = hmac.new(key, raw_body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        raise CryptoPayWebhookSignatureError("webhook signature does not match")


def parse_webhook(payload):
    """Parse a verified Crypto Pay webhook payload into an Update.

    This function does not verify a signature. The application owns request-date
    freshness, idempotency, persistence, HTTP acknowledgement, and business work.
    """
    if isinstance(payload, bytes):
        try:
            payload = payload.decode("utf-8")
        except UnicodeDecodeError as error:
            raise CryptoPayWebhookParseError("webhook body is not UTF-8") from error
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError as error:
            raise CryptoPayWebhookParseError("webhook body is not valid JSON") from error
    if not isinstance(payload, dict):
        raise CryptoPayWebhookParseError("webhook payload must be an object")
    required = ("update_id", "update_type", "request_date", "payload")
    if any(field not in payload for field in required):
        raise CryptoPayWebhookParseError("webhook payload misses required fields")
    return Update(payload)


def parse_and_verify_webhook(raw_body, signature, token):
    """Verify exact raw bytes first, then parse the Crypto Pay Update.

    The caller retains HTTP handling, database-backed idempotency, request-date
    policy, and all business side effects.
    """
    verify_webhook_signature(raw_body, signature, token)
    return parse_webhook(raw_body)
