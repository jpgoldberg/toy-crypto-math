import sys

import pytest
from toy_crypto import sieve


class Fixed:
    """Perhaps better done with fixtures"""

    expected30 = "001101010001010001010001000001"
    """stringy bitarray for primes below 30"""

    ints: list[tuple[int, int]] = [
        (30, int("100000100010100010100010101100", 2)),  # 545925292
        (100, 159085582874019712269820766380),
    ]
    primes100: list[int] = [
        2, 3, 5, 7, 11, 13, 17, 19,
        23, 29, 31, 37, 41, 43, 47,
        53, 59, 61, 67, 71, 73,
        79, 83, 89, 97,
    ]  # fmt: skip
    """primes below 100"""

    sc: sieve.SieveLike

    @classmethod
    def t_30(cls, sc: type[sieve.SieveLike]) -> None:
        sc.reset()
        s30 = sc.from_size(30)
        s30_count = 10

        assert s30.to01() == cls.expected30
        assert s30_count == s30.count

    @classmethod
    def t_count(cls, sc: type[sieve.SieveLike]) -> None:
        s100 = sc.from_size(100)
        result = s100.count
        assert result == len(cls.primes100)

    @classmethod
    def t_primes(cls, sc: type[sieve.SieveLike]) -> None:
        sc.reset()
        s30 = sc.from_size(30)
        expected = [p for p in cls.primes100 if p < 30]

        primes = list(s30.primes())
        assert primes == expected

    @classmethod
    def t_2int(cls, sc: type[sieve.SieveLike]) -> None:
        for size, expected in cls.ints:
            s = sc.from_size(size)
            # s = sc(size)  # We get 'expected zero positional arguments
            i = int(s)
            assert i == expected


class TestBaSieve:
    s_class = sieve.Sieve

    def test_30(self) -> None:
        Fixed.t_30(self.s_class)

    def test_count(self) -> None:
        Fixed.t_count(self.s_class)

    def test_primes(self) -> None:
        Fixed.t_primes(self.s_class)

    def test_2int(self) -> None:
        Fixed.t_2int(self.s_class)


class TestSetSieve:
    s_class = sieve.SetSieve

    def test_30(self) -> None:
        Fixed.t_30(self.s_class)

    def test_count(self) -> None:
        Fixed.t_count(self.s_class)

    def test_primes(self) -> None:
        Fixed.t_primes(self.s_class)

    def test_2int(self) -> None:
        Fixed.t_2int(self.s_class)


class TestIntSieve:
    s_class = sieve.IntSieve

    def test_30(self) -> None:
        Fixed.t_30(self.s_class)

    def test_count(self) -> None:
        Fixed.t_count(self.s_class)

    def test_primes(self) -> None:
        Fixed.t_primes(self.s_class)

    def test_2int(self) -> None:
        Fixed.t_2int(self.s_class)


if __name__ == "__main__":
    sys.exit(pytest.main(args=[__file__]))
