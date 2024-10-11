import sys

import pytest
from toy_crypto import vigenere

Letter = vigenere.Letter
Letters = vigenere.Letters


class TestCryptionDefault:
    """Encryption/decryption tests with default alphabet."""

    default_abc = vigenere.Alphabet(None)

    class TVector:
        def __init__(
            self, key: Letters, ptext: Letters, ctext: Letters
        ) -> None:
            self.key = key
            self.ptext = ptext
            self.ctext = ctext

    vectors = [
        TVector(
            "AAAA",
            "ONCE UPON A MIDNIGHT DREARY",
            "ONCE UPON A MIDNIGHT DREARY",
        ),
        TVector(
            "C",
            "ONCE UPON A MIDNIGHT DREARY",
            "QPEG WRQP C OKFPKIJV FTGCTA",
        ),
        TVector(
            "RAVEN",
            "ONCE UPON A MIDNIGHT DREARY",
            "FNXI LPJR R HMQEIBLG DMINIY",
        ),
    ]

    def test_encrypt(self) -> None:
        for tv in self.vectors:
            cipher = vigenere.Cipher(tv.key, self.default_abc)
            ctext = cipher.encrypt(tv.ptext)

            assert ctext == tv.ctext

    def test_decrypt(self) -> None:
        for tv in self.vectors:
            cipher = vigenere.Cipher(tv.key, self.default_abc)
            ptext = cipher.decrypt(tv.ctext)

            assert ptext == tv.ptext


class TestCryptionPrintable:
    """Encryption/decryption tests with default alphabet."""

    abc = vigenere.Alphabet(prebaked="printable")

    class TVector:
        def __init__(
            self, key: Letters, ptext: Letters, ctext: Letters
        ) -> None:
            self.key = key
            self.ptext = ptext
            self.ctext = ctext

    vectors = [
        TVector(
            [abc.alphabet[0]],
            "ONCE UPON A MIDNIGHT DREARY",
            "ONCE UPON A MIDNIGHT DREARY",
        ),
        TVector(
            "C",
            "ONCE UPON A MIDNIGHT DREARY",
            r"""VBryLMgVBL;LZ1FB1[UILF?y;?b""",
        ),
        TVector(
            "RAVEN",
            "ONCE UPON A MIDNIGHT DREARY",
            r"""gVP=:,+YA:xX$,+2&;'3=.G=VU7""",
        ),
    ]

    def test_encrypt(self) -> None:
        for tv in self.vectors:
            cipher = vigenere.Cipher(tv.key, self.abc)
            ctext = cipher.encrypt(tv.ptext)

            assert ctext == tv.ctext

    def test_decrypt(self) -> None:
        for tv in self.vectors:
            cipher = vigenere.Cipher(tv.key, self.abc)
            ptext = cipher.decrypt(tv.ctext)

            assert ptext == tv.ptext


if __name__ == "__main__":
    sys.exit(pytest.main(args=[__file__]))
