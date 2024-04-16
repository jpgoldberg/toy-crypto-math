from math_utils import Factorization, factor


def test_factor_small() -> None:

    test_vectors: list[tuple[int, Factorization]] = [
        (2, [(2,1)]),
        (10, [(2,1), (5, 1)]),
        (9, [(3, 2)]),
        (1729, [(7, 1), (13, 1), (19, 1)]),
        (75, [(3, 1), (5, 2)]),
        (3557, [(3557, 1)]),
    ]

    for tv in test_vectors:
        n, expected = tv
        assert factor(n) == expected
