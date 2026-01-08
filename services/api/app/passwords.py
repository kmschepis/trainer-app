from __future__ import annotations

import base64
import hashlib
import hmac
import secrets

_ALGO = "pbkdf2_sha256"
_ITERATIONS = 210_000
_SALT_BYTES = 16
_DKLEN = 32
_MAX_PASSWORD_BYTES = 1024


def _b64e(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64d(text: str) -> bytes:
    padding = "=" * (-len(text) % 4)
    return base64.urlsafe_b64decode((text + padding).encode("ascii"))


def hash_password(password: str) -> str:
    if not isinstance(password, str):
        raise ValueError("password must be a string")

    password_bytes = password.encode("utf-8")
    if len(password_bytes) > _MAX_PASSWORD_BYTES:
        raise ValueError("password too long")

    salt = secrets.token_bytes(_SALT_BYTES)
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password_bytes,
        salt,
        _ITERATIONS,
        dklen=_DKLEN,
    )
    return f"{_ALGO}${_ITERATIONS}${_b64e(salt)}${_b64e(derived)}"


def verify_password(password: str, stored: str) -> bool:
    if not isinstance(password, str) or not isinstance(stored, str):
        return False

    try:
        algo, iter_text, salt_text, derived_text = stored.split("$", 3)
        if algo != _ALGO:
            return False
        iterations = int(iter_text)
        salt = _b64d(salt_text)
        expected = _b64d(derived_text)

        password_bytes = password.encode("utf-8")
        if len(password_bytes) > _MAX_PASSWORD_BYTES:
            return False

        actual = hashlib.pbkdf2_hmac(
            "sha256",
            password_bytes,
            salt,
            iterations,
            dklen=len(expected),
        )
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False
