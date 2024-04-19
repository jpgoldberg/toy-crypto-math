import pytest
import sys
from math_utils import FactorList, factor, OLF, miller_rabin, gcd, egcd


class TestFactor:
    def test_factor_small(self) -> None:
        vectors: list[tuple[int, list[tuple[int, int]]]] = [
            (2, [(2, 1)]),
            (10, [(2, 1), (5, 1)]),
            (9, [(3, 2)]),
            (1729, [(7, 1), (13, 1), (19, 1)]),
            (75, [(3, 1), (5, 2)]),
            (3557, [(3557, 1)]),
            (1999162, [(2, 1), (11, 3), (751, 1)]),
            ((2**32) - 1, [(3, 1), (5, 1), (17, 1), (257, 1), (65537, 1)]),
            (
                2**64 - 1,
                [(3, 1), (5, 1), (17, 1), (257, 1), (641, 1), (65537, 1), (6700417, 1)],
            ),
        ]

        for n, expected in vectors:
            assert factor(n) == expected

    def test_OLF(self) -> None:
        vectors: list[tuple[int, int]] = [
            (22171, 1),
            (22171 * 45827 * 5483, 22171 * 5483),
        ]

        for n, expected in vectors:
            assert OLF(n) == expected

    def test_normalize(self) -> None:
        text_vectors: list[tuple[FactorList, FactorList]] = [
            (
                FactorList([(2, 1), (11, 3), (751, 1)]),
                FactorList([(2, 1), (11, 3), (751, 1)]),
            ),
            (
                FactorList([(11, 3), (2, 1), (751, 1)]),
                FactorList([(2, 1), (11, 3), (751, 1)]),
            ),
            (
                FactorList([(11, 1), (2, 1), (11, 1), (751, 1), (11, 1)]),
                FactorList([(2, 1), (11, 3), (751, 1)]),
            ),
        ]
        for tv in text_vectors:
            input, expected = tv
            assert input.normalize() == expected

    def test_factor_large(self) -> None:
        """for input that should trigger Fermat's method,"""

        vectors: list[tuple[int, list[tuple[int, int]]]] = [
            (5483 * 5483, [(5483, 2)]),
            (5483 * 104243 * 11 * 11, [(11, 2), (5483, 1), (104243, 1)]),
            (2**32, [(2, 32)]),
            ((2**31) - 1, [(2147483647, 1)]),
        ]

        for n, expected in vectors:
            assert factor(n) == expected

    def test_phi(self) -> None:
        vectors = [
            ([(3, 1), (5, 1)], 8),
            ([(2, 2), (5, 1)], 8),
            ([(65537, 1)], 65536),
            ([(2, 1), (5, 1), (3, 1)], 8),
        ]
        for f, expected in vectors:
            assert FactorList(f).phi == expected

    def test_n(self) -> None:
        vectors = [
            ([(3, 1), (5, 1)], 15),
            ([(2, 2), (5, 1)], 20),
            ([(65537, 1)], 65537),
        ]
        for input, expected in vectors:
            f = FactorList(input)
            assert f.n == expected
            assert f.value() == expected

    def test_radical(self) -> None:
        vectors = [
            ([(3, 1), (5, 1)], [(3, 1), (5, 1)], 15),
            ([(2, 2), (5, 4)], [(2, 1), (5, 1)], 10),
            ([(2, 32)], [(2, 1)], 2),
        ]

        for input, exp_r, exp_rv in vectors:
            f = FactorList(input)
            assert f.radical() == exp_r
            assert f.radical_value() == exp_rv

    def test_repr(self) -> None:
        vectors = [
            ([(5483, 2)], "5483^2"),
            ([(11, 2), (5483, 1), (104243, 1)], "11^2 * 5483 * 104243"),
            ([(2, 32)], "2^32"),
            ([(2, 6), (3, 3), (5, 3)], "2^6 * 3^3 * 5^3"),
        ]

        for input, expected in vectors:
            f = FactorList(input)
            assert f.__repr__() == expected

    def test_coprimes(self) -> None:
        vectors = [
            (15, [1, 2, 4, 7, 8, 11, 13, 14]),
            (17, list(range(1, 17))),
            (30, [1, 7, 11, 13, 17, 19, 23, 29]),
            (2**5, list(range(1, 2**5, 2))),  # all odd numbers < 2^5
        ]

        for n, relprimes in vectors:
            f = factor(n)
            assert list(f.coprimes()) == relprimes


class TestMath:
    def test_mr(self) -> None:
        vectors = [
            (512461, False),  # a Carmichael number
            (104297, True),
            (1180775137873020977354442912336269, True),
            (
                1025046047436407593990706183629376939000352221561805965005888683119,
                False,
            ),
        ]

        for n, is_prime in vectors:
            assert miller_rabin(n) == is_prime

    def test_gcd(self) -> None:
        vectors = [
            ((5, 50), 5),
            ((18, 12), 6),
        ]

        for input, expected in vectors:
            a, b = input
            assert gcd(a, b) == expected

    def test_egcd(self) -> None:
        vectors = [
            (90, 409),
            (464, 403),
            (308, 463),
            (384, 320),
            (212, 351),
            (382, 472),
            (399, 107),
            (469, 269),
            (44, 163),
            (464, 194),
        ]

        for a, b in vectors:
            g, x, y = egcd(a, b)
            assert g == gcd(a, b)
            assert a * x + b * y == g


if __name__ == "__main__":
    sys.exit(pytest.main())
