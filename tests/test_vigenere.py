import base64
import sys
from pathlib import Path

import pytest
from toy_crypto import vigenere

probabistic = pytest.mark.skip(reason="Probabilistic")

Letter = vigenere.Letter


class TestCryptionDefault:
    """Encryption/decryption tests with default alphabet."""

    default_abc = None

    class TVector:
        def __init__(self, key: str, ptext: str, ctext: str) -> None:
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
            "FNXI HGOI E ZZDIMTYT YVRRRT",
        ),
        TVector(
            "RAVEN",
            "AAAA AAAA A AAAAAAAA AAAAAA",
            "RAVE NRAV E NRAVENRA VENRAV",
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


class TestCryptionCapsOnly:
    """Encryption/decryption tests with CAPS_ONLY alphabet."""

    default_abc = vigenere.Alphabet.CAPS_ONLY

    class TVector:
        def __init__(self, key: str, ptext: str, ctext: str) -> None:
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
            "FNXI HGOI E ZZDIMTYT YVRRRT",
        ),
        TVector(
            "RAVEN",
            "AAAA AAAA A AAAAAAAA AAAAAA",
            "RAVE NRAV E NRAVENRA VENRAV",
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
    """Encryption/decryption tests with printable alphabet."""

    abc = vigenere.Alphabet(prebaked="printable")

    class TVector:
        def __init__(self, key: str, ptext: str, ctext: str) -> None:
            self.key = key
            self.ptext = ptext
            self.ctext = ctext

    vectors = [
        TVector(
            abc.alphabet[0],
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


class TestCryptionCustomAbc:
    """Encryption/decryption tests with custom alphabet."""

    abc = vigenere.Alphabet("0123456789ABCDEF")

    class TVector:
        def __init__(self, key: str, ptext: str, ctext: str) -> None:
            self.key = key
            self.ptext = ptext
            self.ctext = ctext

    vectors = [
        TVector(
            abc[0],
            "DEAD BEEF BAD 5EED",
            "DEAD BEEF BAD 5EED",
        ),
        TVector(
            "2",
            "DEAD BEEF BAD 5EED",
            "F0CF D001 DCF 700F",
        ),
        TVector(
            "BADA55",
            "DEAD BEEF BAD 5EED",
            "8877 0399 842 A98A",
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


class TestCrack:
    cryptopals_filename = "tests/s1c6.txt"
    _encoded = Path(cryptopals_filename).read_text(encoding="ASCII")
    cp_ciphertext: bytes = base64.b64decode(_encoded)
    cp_key = b"TerMinator X: Bring the noiSe"

    @probabistic
    def test_find_keysize(self) -> None:
        # We set number of trial pairs high to reduce chance random failure
        trial_pairs = 8

        scores = vigenere.probable_keysize(
            self.cp_ciphertext,
            min_size=7,
            max_size=35,
            trial_pairs=trial_pairs,
        )

        expected = len(self.cp_key)
        best_length = scores.best
        assert best_length == expected


if __name__ == "__main__":
    sys.exit(pytest.main(args=[__file__]))
