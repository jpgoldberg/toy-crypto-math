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


class TestBirthday:

    n = 23
    d = 365
    p_exact = 38093904702297390785243708291056390518886454060947061 / 75091883268515350125426207425223147563269805908203125

    def test_exact_23(self) -> None:
        p = utils.pbirthday(self.n, self.d, mode="exact")

        assert p == self.p_exact


if __name__ == "__main__":
    sys.exit(pytest.main(args=[__file__]))
