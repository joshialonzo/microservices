import importlib

import pytest

module = importlib.import_module("01_secure_sync_restore")
restore_sync = module.restore_sync


@pytest.mark.parametrize(
    "cipher, key, expected",
    [
        ("KcoTKQ", 2, "IamRIO"),          # problem example
        ("MPSZILEGOIVVERO", 4, "ILOVEHACKERRANK"),  # sample case 0
        ("z", 1, "y"),                    # simple lowercase shift back
        ("A", 1, "Z"),                    # uppercase wrap-around
        ("a", 1, "z"),                    # lowercase wrap-around
        ("abc", 0, "abc"),                # key of 0 is a no-op
        ("abc", 26, "abc"),               # full cycle equals no-op
        ("abc", 27, "zab"),               # key > 26 reduces mod 26
        ("HELLO", 1000000000, None),      # huge key must not overflow/hang
    ],
)
def test_restore_sync(cipher, key, expected):
    result = restore_sync(cipher, key)
    if expected is not None:
        assert result == expected
    # preserve length and case pattern regardless of key
    assert len(result) == len(cipher)
    for original, decrypted in zip(cipher, result):
        assert original.isupper() == decrypted.isupper()
        assert decrypted.isalpha()


def test_huge_key_matches_reduced_key():
    cipher = "SecureSyncRestore"
    assert restore_sync(cipher, 10**9) == restore_sync(cipher, 10**9 % 26)


def test_encrypt_decrypt_roundtrip():
    """Shifting forward by key then restoring should return the original."""
    plain = "AttackAtDawn"
    key = 5
    encrypted = "".join(
        chr((ord(c) - base + key) % 26 + base)
        for c in plain
        for base in [ord("A") if c.isupper() else ord("a")]
    )
    assert restore_sync(encrypted, key) == plain
