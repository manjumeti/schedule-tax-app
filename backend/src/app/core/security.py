"""Security helpers: CSRF token issuance/verification and input sanitization."""
import hashlib
import hmac
import re
import time

from app.core.config import get_settings

_CSRF_TTL_SECONDS = 60 * 60 * 4  # 4 hours
_UNSAFE_HTML_PATTERN = re.compile(r"<\s*(script|iframe|object|embed|style)\b", re.IGNORECASE)


def issue_csrf_token(session_id: str) -> str:
    """Create a signed, time-bound CSRF token bound to a session id (double-submit pattern)."""
    settings = get_settings()
    timestamp = str(int(time.time()))
    payload = f"{session_id}:{timestamp}"
    signature = hmac.new(
        settings.csrf_secret.encode(), payload.encode(), hashlib.sha256
    ).hexdigest()
    return f"{payload}:{signature}"


def verify_csrf_token(token: str, session_id: str) -> bool:
    settings = get_settings()
    try:
        parts = token.split(":")
        if len(parts) != 3:
            return False
        token_session_id, timestamp, signature = parts
        if token_session_id != session_id:
            return False
        if time.time() - int(timestamp) > _CSRF_TTL_SECONDS:
            return False
        expected_payload = f"{token_session_id}:{timestamp}"
        expected_signature = hmac.new(
            settings.csrf_secret.encode(), expected_payload.encode(), hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected_signature, signature)
    except (ValueError, AttributeError):
        return False


def sanitize_text(value: str) -> str:
    """Strip characters/markup that could enable stored XSS in free-text fields.

    Defense in depth only: output encoding on render (React escapes by default)
    remains the primary XSS control. This rejects obviously dangerous markup.
    """
    if _UNSAFE_HTML_PATTERN.search(value):
        raise ValueError("Field contains disallowed markup")
    return value.strip()
