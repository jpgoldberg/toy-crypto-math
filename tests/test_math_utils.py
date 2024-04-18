import pytest
import sys
from math_utils import FactorList, factor, OLF, miller_rabin


def test_factor_small() -> None:
    test_vectors: list[tuple[int, list[tuple[int, int]]]] = [
        (2, [(2, 1)]),
        (10, [(2, 1), (5, 1)]),
        (9, [(3, 2)]),
        (1729, [(7, 1), (13, 1), (19, 1)]),
        (75, [(3, 1), (5, 2)]),
        (3557, [(3557, 1)]),
        (1999162, [(2, 1), (11, 3), (751, 1)]),
    ]

    for n, expected in test_vectors:
        assert factor(n) == expected


def test_OLF() -> None:
    test_vectors: list[tuple[int, int]] = [
        (22171, 1),
        (22171 * 45827 * 5483, 22171 * 5483),
    ]

    for n, expected in test_vectors:
        assert OLF(n) == expected


def test_normalize() -> None:
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


def test_factor_large() -> None:
    """for input that should trigger Fermat's method,"""

    test_vectors: list[tuple[int, list[tuple[int, int]]]] = [
        (5483 * 5483, [(5483, 2)]),
        (5483 * 104243 * 11 * 11, [(11, 2), (5483, 1), (104243, 1)]),
        ((2**32) - 1, [(3, 1), (5, 1), (17, 1), (257, 1), (65537, 1)]),
        (2**32, [(2, 32)]),
        ((2**31) - 1, [(2147483647, 1)]),
        (
            2**64 - 1,
            [(3, 1), (5, 1), (17, 1), (257, 1), (641, 1),
             (65537, 1), (6700417, 1)],
        ),
    ]

    for n, expected in test_vectors:
        assert factor(n) == expected


def test_phi() -> None:
    test_vectors = [
        ([(3, 1), (5, 1)], 8),
        ([(2, 2), (5, 1)], 8),
        ([(65537, 1)], 65536),
    ]
    for f, expected in test_vectors:
        assert FactorList(f).phi == expected


def test_n() -> None:
    test_vectors = [
        ([(3, 1), (5, 1)], 15),
        ([(2, 2), (5, 1)], 20),
        ([(65537, 1)], 65537),
    ]
    for input, expected in test_vectors:
        f = FactorList(input)
        assert f.n == expected
        assert f.value() == expected


def test_radical() -> None:
    test_vectors = [
        (
            [(3, 1), (5, 1)],
            [(3, 1), (5, 1)],
            15
        ),
        (
            [(2, 2), (5, 4)],
            [(2, 1), (5, 1)],
            10
        ),
        (
            [(2, 32)],
            [(2, 1)],
            2
        ),
    ]

    for input, exp_r, exp_rv in test_vectors:
        f = FactorList(input)
        assert f.radical() == exp_r
        assert f.radical_value() == exp_rv


def test_repr() -> None:
    test_vectors = [
        ([(5483, 2)], '5483^2'),
        ([(11, 2), (5483, 1), (104243, 1)], '11^2 * 5483 * 104243'),
        ([(2, 32)], '2^32'),
        ([(2, 6), (3, 3), (5, 3)], '2^6 * 3^3 * 5^3'),
    ]

    for input, expected in test_vectors:
        f = FactorList(input)
        assert f.__repr__() == expected


def test_coprimes() -> None:
    test_vectors = [
        (15, [1, 2, 4, 7, 8, 11, 13, 14]),
        (17, list(range(1, 17))),
    ]

    for n, relprimes in test_vectors:
        f = factor(n)
        assert list(f.coprimes()) == relprimes


def test_mr() -> None:
    test_vectors = [
        (1729, False),
        (104297, True),
        (1180775137873020977354442912336269, True),
        (1025046047436407593990706183629376939000352221561805965005888683119,
         False),
    ]

    for n, is_prime in test_vectors:
        assert miller_rabin(n) == is_prime


if __name__ == '__main__':
    sys.exit(pytest.main())
