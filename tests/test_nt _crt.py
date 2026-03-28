import itertools
from collections.abc import Sequence
import sys

import pytest
from toy_crypto.nt import crt


class TestSolve:
    @pytest.mark.parametrize(
        "moduli, remainders, expected",
        [
            ((4, 9, 25), (3, 1, 14), 739),
            ((3, 4, 7), (1, 1, 0), 49),
            ((5, 7, 11), (2, 3, 10), 87),
            ((2, 3, 5), (0, 0, 0), 30),
        ],
    )
    def test_solve_coprime(
        self, moduli: Sequence[int], remainders: Sequence[int], expected: int
    ) -> None:
        result = crt.solve(moduli, remainders)
        assert result == expected

    @pytest.mark.parametrize(
        "moduli, remainders, expected",
        [((4, 6), (2, 0), 12), ((4, 6), (3, 0), None)],
    )
    def test_solve_common_factor(
        self,
        moduli: Sequence[int],
        remainders: Sequence[int],
        expected: int | None,
    ) -> None:
        result = crt.solve(moduli, remainders)
        assert result == expected


class TestRing:
    m_4_9_25: Sequence[int] = (4, 9, 25)
    r_4_9_25: list[tuple[Sequence[int], int]] = [
        ((3, 1, 14), 739),
        ((57, 55, 68), 793),
        ((369, 123, 1722), 897),
        ((1, 1, 1), 1),
        ((0, 0, 0), 900),
        ((3, 8, 24), 899),
    ]

    @pytest.mark.parametrize(
        "remainders, expected",
        r_4_9_25,
    )
    def test_solve_4_9_25(
        self, remainders: Sequence[int], expected: int
    ) -> None:
        moduli = (4, 9, 25)
        ring = crt.Ring(moduli)

        result = ring.to_int(remainders)
        assert result == expected

    def test_modulus(self) -> None:
        moduli = (4, 9, 25)
        ring = crt.Ring(moduli)
        expected_product = 900
        assert ring.modulus == expected_product

    def test_mul_4_9_25(self) -> None:
        integers = [0, 1, 2, 3, 739, 54, 897, 899, 900]
        ring = crt.Ring((4, 9, 25))
        lcm = ring.modulus

        for a, b in itertools.product(integers, repeat=2):
            m_a = ring.element(a)
            m_b = ring.element(b)
            prod = m_a * m_b
            assert (a * b) % lcm == int(prod) % lcm


if __name__ == "__main__":
    sys.exit(pytest.main(args=[__file__]))
