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

    def test_bits(self) -> None:
        vectors = [
            (0b1101, [1, 0, 1, 1]),
            (1, [1]),
            (0, []),
            (0o644, [0, 0, 1, 0, 0, 1, 0, 1, 1]),
            (65537, [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]),
        ]
        for n, expected in vectors:
            bits = [bit for bit in utils.lsb_to_msb(n)]
            assert bits == expected

    def test_hamming(self) -> None:
        s1 = b"this is a test"
        s2 = b"wokka wokka!!!"

        hd = utils.hamming_distance(s1, s2)
        assert hd == 37


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


class TestIntBits:
    """Tests for the bit manipulation of ints"""

    vectors: list[tuple[int, tuple[int, bool], int]] = [
        (0, (0, True), 1),
        (1, (0, True), 1),
        (1, (0, False), 0),
        (5, (1, True), 7),
        (5, (3, True), 13),
        (16, (4, False), 0),
        (16, (4, True), 16),
        (15, (2, False), 11),
        (15, (3, False), 7),
    ]

    def test_set_true(self) -> None:
        for left, (bit, value), right in self.vectors:
            if not value:
                left, right = right, left
            result = utils.set_bit(left, bit, True)
            assert result == right

    def test_set_false(self) -> None:
        for left, (bit, value), right in self.vectors:
            if value:
                # left, right = right, left
                continue
            result = utils.set_bit(left, bit, False)
            assert result == right

    def test_index(self) -> None:
        vectors: list[tuple[int | str, dict[int, int | None]]] = [
            ("11010", {1: 1, 2: 3, 3: 4, 4: None}),
            (
                0b100010100010100010101100,
                {1: 2, 2: 3, 3: 5, 4: 7, 5: 11, 6: 13, 7: 17, 8: 19, 9: 23},
            ),
        ]

        for n, d in vectors:
            if isinstance(n, str):
                n = int(n, 2)
            for k, expected in d.items():
                result = utils.bit_index(n, k, 1)
                assert result == expected


if __name__ == "__main__":
    sys.exit(pytest.main(args=[__file__]))
