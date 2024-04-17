from math_utils import FactorList, factor, OLF


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

    for tv in test_vectors:
        n, expected = tv
        assert factor(n) == expected


def test_OLF() -> None:
    test_vectors: list[tuple[int, int]] = [
        (22171, 1),
        (22171 * 45827 * 5483, 22171 * 5483),
    ]

    for tv in test_vectors:
        n, expected = tv
        assert OLF(n) == expected
