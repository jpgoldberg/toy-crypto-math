import sys

import pytest
from toy_crypto import types


primes100 = [
    2, 3, 5, 7, 11, 13, 17, 19,
    23, 29, 31, 37, 41, 43, 47,
    53, 59, 61, 67, 71, 73,
    79, 83, 89, 97,
]  # fmt: skip


class TestPyBitArray:
    def test_zeros(self) -> None:
        length = 50
        ba = types.PyBitArray(length, fill_bit=0)

        for idx in range(length):
            assert ba[idx] == 0

    def test_ones(self) -> None:
        length = 50
        ba = types.PyBitArray(length, fill_bit=1)

        for idx in range(length):
            assert ba[idx] == 1

    def test_set(self) -> None:
        ba = types.PyBitArray(100, fill_bit=0)
        for p in primes100:
            ba[p] = 1

        for i in range(100):
            if i in primes100:
                assert ba[i] == 1
            else:
                assert ba[i] == 0

    def test_unset(self) -> None:
        ba = types.PyBitArray(100, fill_bit=1)

        composites = set(range(100)) - set(primes100)
        for c in composites:
            ba[c] = 0

        for i in range(100):
            if i in primes100:
                assert ba[i] == 1
            else:
                assert ba[i] == 0


if __name__ == "__main__":
    sys.exit(pytest.main(args=[__file__]))
