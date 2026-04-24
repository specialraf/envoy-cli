"""Tests for envoy.crypto encryption/decryption utilities."""

import pytest
from envoy.crypto import encrypt, decrypt


PASSWORD = "super-secret-passphrase"
PLAINTEXT = "DB_HOST=localhost\nDB_PORT=5432\nSECRET_KEY=abc123"


def test_encrypt_returns_bytes():
    result = encrypt(PLAINTEXT, PASSWORD)
    assert isinstance(result, bytes)


def test_encrypt_different_each_call():
    """Each call should produce a different ciphertext (random salt)."""
    cipher1 = encrypt(PLAINTEXT, PASSWORD)
    cipher2 = encrypt(PLAINTEXT, PASSWORD)
    assert cipher1 != cipher2


def test_roundtrip():
    """Encrypting then decrypting should return the original plaintext."""
    ciphertext = encrypt(PLAINTEXT, PASSWORD)
    recovered = decrypt(ciphertext, PASSWORD)
    assert recovered == PLAINTEXT


def test_wrong_password_raises():
    ciphertext = encrypt(PLAINTEXT, PASSWORD)
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt(ciphertext, "wrong-password")


def test_corrupted_data_raises():
    ciphertext = bytearray(encrypt(PLAINTEXT, PASSWORD))
    ciphertext[20] ^= 0xFF  # flip a byte in the token
    with pytest.raises(ValueError):
        decrypt(bytes(ciphertext), PASSWORD)


def test_too_short_data_raises():
    with pytest.raises(ValueError, match="too short"):
        decrypt(b"short", PASSWORD)


def test_empty_plaintext_roundtrip():
    ciphertext = encrypt("", PASSWORD)
    assert decrypt(ciphertext, PASSWORD) == ""


def test_unicode_plaintext_roundtrip():
    unicode_text = "API_KEY=clésecrète\nEMOJI=🔑"
    ciphertext = encrypt(unicode_text, PASSWORD)
    assert decrypt(ciphertext, PASSWORD) == unicode_text
