import pytest
import sys
import math
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

    vectors = [
        (23, 365, 38093904702297390785243708291056390518886454060947061 / 75091883268515350125426207425223147563269805908203125),
        (10, 365, 2689423743942044098153/22996713557917153515625),

    ]

    n = 23
    d = 365
    p_exact = 38093904702297390785243708291056390518886454060947061 / 75091883268515350125426207425223147563269805908203125

    def test_pbirthday(self) -> None:

        for n, d, expected in self.vectors:
            p = utils.pbirthday(n, d, mode="exact")
            assert p == expected

    def test_qbrithday(self) -> None:

        for expected_n, d, p in self.vectors:
            n = utils.qbirthday(p, d)
            assert n == expected_n

    def test_inverse_365(self) -> None:

        d = 365

        for n in range(10, 360, 10):
            p = utils.pbirthday(n, d)

            # This will go very badly when p gets large
            if p > 0.99:
                break
            n2 = utils.qbirthday(p, d)

            assert math.isclose(n, n2, rel_tol=0.5)


if __name__ == "__main__":
    sys.exit(pytest.main(args=[__file__]))
