import sys

import pytest
from toy_crypto import utils


class TestUtils:
    def test_bits(self) -> None:
        vectors = [
            (0b1101, [1, 0, 1, 1]),
            (1, [1]),
            (0, []),
            (0o644, [0, 0, 1, 0, 0, 1, 0, 1, 1]),
        ]
        for n, expected in vectors:
            bits = [bit for bit in utils.lsb_to_msb(n)]
            assert bits == expected

    def test_xor(self) -> None:
        vectors = [
            (b"dusk", b"dawn", bytes.fromhex("00 14 04 05")),
            (
                b"Attack at dawn!",
                bytes(10) + bytes.fromhex("00 14 04 05 00"),
                b"Attack at dusk!",
            ),
        ]

        for x, y, pad in vectors:
            r = utils.xor(x, y)
            assert r == pad


if __name__ == "__main__":
    sys.exit(pytest.main(args=[__file__]))
