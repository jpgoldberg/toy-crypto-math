import itertools
import math
import sys
from typing import NamedTuple

import pytest
from toy_crypto import birthday


class HashVector(NamedTuple):
    bits: int
    p: float
    n: int


class TestBirthday:
    vectors: list[tuple[int, int, float]] = [
        (
            23,
            365,
            38093904702297390785243708291056390518886454060947061
            / 75091883268515350125426207425223147563269805908203125,
        ),
        (10, 365, 2689423743942044098153 / 22996713557917153515625),
    ]

    # data from table in https://en.wikipedia.org/wiki/Birthday_attack
    # tuples are (bits, prob, n)
    _table_p: list[float] = [
        1e-18, 1e-15, 1e-12, 1e-9, 1e-6,
        0.001, 0.01, 0.25, 0.50, 0.75,
    ]  # fmt: skip

    hash_vectors: list[HashVector] = []
    """Data from Wikipedia Birthday Attack article."""
    hv16 = [
        HashVector(16, p, int(n))
        for p, n in zip(_table_p, [2, 2, 2, 2, 2, 11, 36, 190, 300, 430])
    ]
    hash_vectors.extend(hv16)

    hv32 = [
        HashVector(32, p, int(n))
        for p, n in zip(
            _table_p, [2, 2, 2, 3, 93, 2900, 9300, 50_000, 77_000, 110_000]
        )
    ]
    hash_vectors.extend(hv32)

    hv64 = [
        HashVector(64, p, int(n))
        for p, n in zip(
            _table_p,
            [
                # 7,  # Original data has 6.
                6,
                190,
                6100,
                190_000,
                6_100_000,
                1.9e8,
                6.1e8,
                3.3e9,
                5.1e9,
                7.2e9,
            ],  # fmt: skip
        )
    ]
    hash_vectors.extend(hv64)

    hv96 = [
        HashVector(96, p, int(n))
        for p, n in zip(
            _table_p,
            [
                4.0e5,
                1.3e7,
                4.0e8,
                1.3e10,
                4.0e11,
                1.3e13,
                4.0e13,
                2.1e14,
                3.3e14,
                4.7e14,
            ],  # fmt: skip
        )
    ]
    hash_vectors.extend(hv96)

    hv128 = [
        HashVector(128, p, int(n))
        for p, n in zip(
            _table_p,
            [
                2.6e10,
                8.2e11,
                2.6e13,
                8.2e14,
                2.6e16,
                8.3e17,
                2.6e18,
                1.4e19,
                2.2e19,
                3.1e19,
            ],  # fmt: skip
        )
    ]
    hash_vectors.extend(hv128)

    hv192 = [
        HashVector(192, p, int(n))
        for p, n in zip(
            _table_p,
            [
                1.1e20,
                3.7e21,
                1.1e23,
                3.5e24,
                1.1e26,
                3.5e27,
                1.1e28,
                6.0e28,
                9.3e28,
                1.3e29,
            ],  # fmt: skip
        )
    ]
    hash_vectors.extend(hv192)

    hv256 = [
        HashVector(256, p, int(n))
        for p, n in zip(
            _table_p,
            [
                4.8e29,
                1.5e31,
                4.8e32,
                1.5e34,
                4.8e35,
                1.5e37,
                4.8e37,
                2.6e38,
                4.0e38,
                5.7e38,
            ],  # fmt: skip
        )
    ]
    hash_vectors.extend(hv256)

    k_p50_c365_vectors = [
        (2, 23), (3, 88), (4, 187), (5, 313),
        (6, 460), (7, 623), (8, 798), (9, 985),
        (10, 1181), (11, 1385), (12, 1596), (13, 1813),
    ]  # fmt: skip
    """(k, n) s.t. Q(prob=0.5, classes=365, coincident=k) ==  n.

    From DM69 table 3
    """

    @staticmethod
    @pytest.mark.parametrize(
        "n, d, expected",
        vectors,
    )
    def test_pbirthday(n: int, d: int, expected: float) -> None:
        p = birthday.probability(n, d, mode="exact")
        assert math.isclose(p, expected)

    @staticmethod
    @pytest.mark.parametrize(
        "expected, d, p",
        vectors,
    )
    def test_qbrithday(d: int, p: float, expected: int) -> None:
        n = birthday.quantile(p, d)
        assert n == expected

    @staticmethod
    @pytest.mark.parametrize("n", range(10, 360, 10))
    def test_inverse_365(n: int) -> None:
        d = 365
        p = birthday.probability(n, d)
        if p > birthday.MAX_QBIRTHDAY_P:
            return
        n2 = birthday.quantile(p, d)
        assert n == n2

    @staticmethod
    @pytest.mark.parametrize(
        "bits, p, n",
        # hash_vectors,
        # 8 failures for fewer than 64 bits
        list(
            itertools.filterfalse(
                lambda t: t[0] < 64,  # type: ignore[index]
                hash_vectors,
            )
        ),
    )
    def test_wp_data_p(bits: int, p: float, n: int) -> None:
        classes = int(1 << bits)
        my_p = birthday.probability(n, classes=classes)
        rel_delta = abs(my_p - p) / p
        assert math.isclose(p, my_p, rel_tol=0.1), (
            f"p: {p}; my_p: {my_p}; rel diff: {rel_delta}"
        )

    @staticmethod
    @pytest.mark.parametrize(
        "bits, p, n",
        itertools.filterfalse(
            lambda v: v[2] == 6,  # type: ignore[index]
            hash_vectors,
        ),
    )
    def test_wp_data_q(bits: int, p: float, n: int) -> None:
        c = int(1 << bits)
        my_n = birthday.quantile(p, c)
        assert math.isclose(n, my_n, rel_tol=0.1), f"n: {n}; my_n: {my_n}"

    @staticmethod
    @pytest.mark.parametrize("k, n", k_p50_c365_vectors)
    def test_k_p(k: int, n: int) -> None:
        expected_p = 0.5
        c = 365
        wiggle_room = 0.01  # because P always uses approximation when k > 2

        calculated_p = birthday.probability(n, c, k)
        p_below = birthday.probability(n - 1, c, k)

        assert calculated_p + wiggle_room >= expected_p
        assert p_below < expected_p + wiggle_room

    @pytest.mark.parametrize("k, expected_n", k_p50_c365_vectors)
    def test_k_q(self, k: int, expected_n: int) -> None:
        calculated_n = birthday.quantile(0.5, 365, k)
        assert math.isclose(calculated_n, expected_n, rel_tol=0.01)


class TestSpecialCasesP:
    def test_exsct_n_equal_c(self) -> None:
        p = birthday.probability(n=20, classes=20, mode="exact")
        assert p == 1.0

    def test_approx_n_equal_c(self) -> None:
        p = birthday.probability(n=20, classes=20, mode="approximate")
        assert p == 1.0

    def test_n_gt_c(self) -> None:
        p = birthday.probability(n=20, classes=19, mode="exact")
        assert p == 1.0

    def test_n_gt_ck(self) -> None:
        p = birthday.probability(
            n=20, classes=10, coincident=3, mode="approximate"
        )
        assert p == 1.0

    def test_exact_k_lt_two(self) -> None:
        p = birthday.probability(n=23, classes=365, coincident=1, mode="exact")
        assert p == 1.0

    def test_approx_k_lt_two(self) -> None:
        p = birthday.probability(
            n=23, classes=365, coincident=1, mode="approximate"
        )
        assert p == 1.0


class TestSpecialCasesQ:
    HIGH_P = (1.0 + birthday.MAX_QBIRTHDAY_P) / 2.0

    def test_p_is_0(self) -> None:
        q = birthday.quantile(prob=0.0)
        assert q == 1.0

    @pytest.mark.parametrize("c", range(100, 5000, 100))
    @pytest.mark.parametrize("k", (2, 35, 5))
    def test_big_p(self, c: int, k: int) -> None:
        q = birthday.quantile(prob=self.HIGH_P, classes=c, coincident=k)
        assert q == c * (k - 1) + 1


if __name__ == "__main__":
    sys.exit(pytest.main(args=[__file__]))
