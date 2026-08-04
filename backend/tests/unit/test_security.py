"""Unit tests for CSRF token issuance/verification and text sanitization."""
import pytest

from app.core.security import issue_csrf_token, sanitize_text, verify_csrf_token


def test_csrf_token_round_trip():
    token = issue_csrf_token("session-123")
    assert verify_csrf_token(token, "session-123") is True


def test_csrf_token_rejected_for_wrong_session():
    token = issue_csrf_token("session-123")
    assert verify_csrf_token(token, "session-456") is False


def test_csrf_token_rejected_when_tampered():
    token = issue_csrf_token("session-123")
    tampered = token[:-1] + ("0" if token[-1] != "0" else "1")
    assert verify_csrf_token(tampered, "session-123") is False


def test_csrf_token_rejected_when_malformed():
    assert verify_csrf_token("not-a-token", "session-123") is False


def test_sanitize_text_strips_whitespace():
    assert sanitize_text("  hello  ") == "hello"


def test_sanitize_text_rejects_script_tags():
    with pytest.raises(ValueError):
        sanitize_text("<script>alert(1)</script>")
