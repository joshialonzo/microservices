"""Secure Sync Restore.

Decrypt a Caesar-cipher string by shifting each letter *back* by `key`
positions, wrapping around the alphabet. Case is preserved; only English
letters appear in the input.

Constraints:
    1 <= len(cipher) <= 2 * 10**5
    0 <= key <= 10**9   (so reduce the key modulo 26)
"""


def alphabet_lowercase() -> str:
    return "abcdefghijklmnopqrstuvwxyz"


def alphabet_uppercase() -> str:
    return "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def shifted_alphabet_lowercase(key: int) -> str:
    """Return the lowercase alphabet shifted by `key` positions."""
    key %= 26
    first_key_letters = alphabet_lowercase()[:key]
    last_letters = alphabet_lowercase()[key:]
    return last_letters + first_key_letters


def shifted_alphabet_uppercase(key: int) -> str:
    """Return the uppercase alphabet shifted by `key` positions."""
    key %= 26
    first_key_letters = alphabet_uppercase()[:key]
    last_letters = alphabet_uppercase()[key:]
    return last_letters + first_key_letters


def zip_lowercase_alphabets(key: int) -> zip:
    """Map each shifted (cipher) letter back to its original."""
    return zip(shifted_alphabet_lowercase(key), alphabet_lowercase())


def zip_uppercase_alphabets(key: int) -> zip:
    """Map each shifted (cipher) letter back to its original."""
    return zip(shifted_alphabet_uppercase(key), alphabet_uppercase())


def merge_zipped_alphabets(key: int) -> dict:
    """Return a dict mapping each letter to its shifted version."""
    return dict(zip_lowercase_alphabets(key)) | dict(zip_uppercase_alphabets(key))


def restore_sync(cipher: str, key: int) -> str:
    """Return the decrypted string.

    TODO: implement the decryption.

    Hints:
      - key can be huge, so use `key % 26`.
      - for a lowercase char: base = ord('a'); new = (ord(c) - base - key) % 26 + base
      - for an uppercase char: base = ord('A')

    """
    # reduce key modulo 26
    key = key % 26

    # create a mapping of each letter to its shifted version
    shifted_alphabet = merge_zipped_alphabets(key)

    # decrypt the cipher by replacing each letter with its shifted version
    decrypted = "".join(shifted_alphabet.get(c, c) for c in cipher)

    return decrypted
