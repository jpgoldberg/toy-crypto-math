import pytest
import sys
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


if __name__ == "__main__":
    sys.exit(pytest.main(args=[__file__]))
