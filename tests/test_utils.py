import sys

import pytest
from collections.abc import Iterator
from toy_crypto import utils
from toy_crypto.types import Byte


class TestUtils:
    def test_digit_count(self) -> None:
        i_e61 = pow(10, 61)  # because '1e61` does floating point operations
        vectors = [
            (999, 3),
            (1000, 4),
            (1001, 4),
            (i_e61, 62),
            (i_e61 - 1, 61),
            (i_e61 + 1, 62),
            (-999, 3),
            (0, 1),
            (-0, 1),
        ]
        for n, expected in vectors:
            d = utils.digit_count(n)
            assert d == expected


class TestXor:
    def test_xor(self) -> None:
        vectors = [
            (b"dusk", b"dawn", bytes.fromhex("00 14 04 05")),
            (
                b"Attack at dawn!",
                bytes(10) + bytes.fromhex("00 14 04 05 00"),
                b"Attack at dusk!",
            ),
            (
                bytes(15),
                bytes.fromhex("00 01 02"),
                bytes.fromhex("00 01 02") * 5,
            ),
        ]

        for x, y, pad in vectors:
            r = utils.xor(x, y)
            assert r == pad

    def test_iter(self) -> None:
        pad = bytes.fromhex("00 36 5C")
        p_modulus = len(pad)
        single = list(range(0, 256))
        s_modulus = len(single)
        message: Iterator[Byte] = iter(single * 10)

        iter_xor = utils.Xor(message, pad)

        m_idx = 0
        p_idx = 0
        for b in iter_xor:
            expected = (m_idx % s_modulus) ^ pad[p_idx]
            assert b == expected
            m_idx += 1
            p_idx = (p_idx + 1) % p_modulus

        assert m_idx == s_modulus * 10


class TestRsa29Encoding:
    vectors: list[tuple[str, int]] = [
        ("ITS ALL GREEK TO ME", 9201900011212000718050511002015001305),
        (
            "THE MAGIC WORDS ARE SQUEAMISH OSSIFRAGE",
            200805001301070903002315180419000118050019172105011309190800151919090618010705,
        ),
    ]

    def test_encode(self) -> None:
        for s, n in self.vectors:
            encoded = utils.Rsa129.encode(s)
            assert encoded == n

    def test_decode(self) -> None:
        for s, n in self.vectors:
            decoded = utils.Rsa129.decode(n)
            assert decoded == s


if __name__ == "__main__":
    sys.exit(pytest.main(args=[__file__]))
