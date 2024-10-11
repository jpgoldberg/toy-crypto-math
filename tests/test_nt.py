import sys
from typing import NamedTuple

import pytest
from toy_crypto import nt, redundent


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
                [
                    (3, 1),
                    (5, 1),
                    (17, 1),
                    (257, 1),
                    (641, 1),
                    (65537, 1),
                    (6700417, 1),
                ],
            ),
            (3 * 5 * 5 * 7, [(3, 1), (5, 2), (7, 1)]),
        ]

        for n, expected in vectors:
            assert nt.factor(n) == expected

    def test_OLF(self) -> None:
        vectors: list[tuple[int, int]] = [
            (22171, 1),
            (22171 * 45827 * 5483, 22171 * 5483),
        ]

        for n, expected in vectors:
            assert redundent.OLF(n) == expected

    def test_normalize(self) -> None:
        text_vectors: list[tuple[nt.FactorList, nt.FactorList]] = [
            (
                nt.FactorList([(2, 1), (11, 3), (751, 1)]),
                nt.FactorList([(2, 1), (11, 3), (751, 1)]),
            ),
            (
                nt.FactorList([(11, 3), (2, 1), (751, 1)]),
                nt.FactorList([(2, 1), (11, 3), (751, 1)]),
            ),
            (
                nt.FactorList([(11, 1), (2, 1), (11, 1), (751, 1), (11, 1)]),
                nt.FactorList([(2, 1), (11, 3), (751, 1)]),
            ),
        ]
        for tv in text_vectors:
            input, expected = tv
            assert input.normalize() == expected

    def test_add(self) -> None:
        # Mostly we are checking that result is normalized
        vectors = [
            (
                nt.FactorList([(11, 1), (2, 1), (11, 1)]),
                nt.FactorList([(751, 1), (11, 1)]),
                nt.FactorList([(2, 1), (11, 3), (751, 1)]),
            ),
            (
                nt.FactorList([(11, 1), (2, 1), (11, 1)]),
                nt.FactorList([]),
                nt.FactorList([(2, 1), (11, 2)]),
            ),
        ]
        for a, b, expected in vectors:
            assert a + b == expected
            assert b + a == expected

    def test_factor_large(self) -> None:
        """for input that should trigger Fermat's method,"""

        vectors: list[tuple[int, list[tuple[int, int]]]] = [
            (5483 * 5483, [(5483, 2)]),
            (5483 * 104243 * 11 * 11, [(11, 2), (5483, 1), (104243, 1)]),
            (2**32, [(2, 32)]),
            ((2**31) - 1, [(2147483647, 1)]),
            (104243 * 2147483647 * 2147483647, [(104243, 1), (2147483647, 2)]),
        ]
        for n, expected in vectors:
            assert nt.factor(n) == expected

    def test_phi(self) -> None:
        vectors = [
            ([(3, 1), (5, 1)], 8),
            ([(2, 2), (5, 1)], 8),
            ([(65537, 1)], 65536),
            ([(2, 1), (5, 1), (3, 1)], 8),
        ]
        for f, expected in vectors:
            assert nt.FactorList(f).phi == expected

    def test_n(self) -> None:
        vectors = [
            ([(3, 1), (5, 1)], 15),
            ([(2, 2), (5, 1)], 20),
            ([(65537, 1)], 65537),
        ]
        for input, expected in vectors:
            f = nt.FactorList(input)
            assert f.n == expected
            assert f.value() == expected

    def test_radical(self) -> None:
        vectors = [
            ([(3, 1), (5, 1)], [(3, 1), (5, 1)], 15),
            ([(2, 2), (5, 4)], [(2, 1), (5, 1)], 10),
            ([(2, 32)], [(2, 1)], 2),
        ]

        for input, exp_r, exp_rv in vectors:
            f = nt.FactorList(input)
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
            f = nt.FactorList(input)
            assert f.__repr__() == expected

    def test_coprimes(self) -> None:
        vectors = [
            (15, [1, 2, 4, 7, 8, 11, 13, 14]),
            (17, list(range(1, 17))),
            (30, [1, 7, 11, 13, 17, 19, 23, 29]),
            (2**5, list(range(1, 2**5, 2))),  # all odd numbers < 2^5
        ]

        for n, relprimes in vectors:
            f = nt.factor(n)
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
            assert nt.isprime(n) == is_prime

    def test_gcd(self) -> None:
        vectors = [
            ((5, 50), 5),
            ((18, 12), 6),
            ((90, 409), 1),
            ((464, 403), 1),
            ((308, 463), 1),
            ((384, 320), 64),
            ((382, 472), 2),
        ]

        for input, expected in vectors:
            a, b = input
            assert nt.gcd(a, b) == expected

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
            g, x, y = nt.egcd(a, b)
            assert g == nt.gcd(a, b)
            assert a * x + b * y == g

    def test_mod_sqrt(self) -> None:
        class TestVector(NamedTuple):
            a: int
            m: int
            expected: list[int]

        tests = [
            TestVector(58, 101, [82, 19]),
            TestVector(26, 101, []),
            TestVector(111, 113, [87, 26]),
            TestVector(55, 113, []),
            TestVector(30, 103, [37, 103 - 37]),
            TestVector(31, 103, []),
        ]

        for a, m, expected in tests:
            # first some verification of the roots in test vectors
            if expected:
                for root in expected:
                    assert a == root * root % m

            e: list[int] = [] if expected is None else sorted(list(expected))
            ret = nt.mod_sqrt(a, m)
            r: list[int] = [] if ret is None else sorted(list(ret))
            assert e == r

    def test_modinv(self) -> None:
        p = 868112830765445632873217196988651
        q = 1180775137873020977354442912336269

        p_inv = nt.modinv(p, q)
        q_inv = nt.modinv(q, p)

        assert (p_inv * p) % q == 1
        assert (q_inv * q) % p == 1

        assert p_inv > 0
        assert p_inv < q

        assert q_inv > 0
        assert q_inv < p

    def test_isqrt(self) -> None:
        p = 868112830765445632873217196988651
        vectors = [
            (2_000_000, 1414),
            (99, 9),  # check when n+1 is a a perfect square
            (100, 10),
            (1, 1),
            (0, 0),
            (p * p, p),
            ((p * p) + 1, p),
        ]

        for n, expected in vectors:
            assert nt.isqrt(n) == expected


class TestSieve:
    def test_sieve_30(self) -> None:
        s30 = nt.Sieve(30)
        expected = "001101010001010001010001000001"
        s30_count = 10

        assert s30.to01() == expected
        assert s30_count == s30.count

        # test that s30 still behaves as if it is 30 even if we create
        # a larger internal sieve
        s200 = nt.Sieve(200)

        # test that the larger sieve was indeed created
        s200_count = 46  # primes below 200
        assert s200.count == s200_count

        # large underlying sieve leaves s30's behavior unchanged
        assert s30.to01() == expected


if __name__ == "__main__":
    sys.exit(pytest.main(args=[__file__]))
