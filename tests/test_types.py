import sys

import pytest
from toy_crypto import types


@pytest.fixture
def sets() -> dict[str, set[int]]:
    sets: dict[str, set[int]] = dict()
    sets["universe"] = set(range(100))

    sets["primes"] = {
        2, 3, 5, 7, 11, 13, 17, 19,
        23, 29, 31, 37, 41, 43, 47,
        53, 59, 61, 67, 71, 73,
        79, 83, 89, 97,
    }  # fmt: skip

    sets.update(
        {f"multiples_{n}": set(range(0, 100, n)) for n in range(2, 12)}
    )

    return sets


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

    def test_set(self, sets: dict[str, set[int]]) -> None:
        universe = sets["universe"]
        size = len(universe)

        for name, test_set in sets.items():
            ba = types.PyBitArray(size, fill_bit=0)
            for p in test_set:
                ba[p] = 1

            for i in universe:
                if i in test_set:
                    assert ba[i] == 1, f"set: {name}; i: {i}"
                else:
                    assert ba[i] == 0, f"set: {name}; i: {i}"

    def test_unset(self, sets: dict[str, set[int]]) -> None:
        universe = sets["universe"]
        size = len(universe)

        for name, test_set in sets.items():
            ba = types.PyBitArray(size, fill_bit=1)

            complement = universe - test_set
            for c in complement:
                ba[c] = 0

            for i in universe:
                if i in test_set:
                    assert ba[i] == 1, f"set: {name}; i: {i}"
                else:
                    assert ba[i] == 0, f"set: {name}; i: {i}"


if __name__ == "__main__":
    sys.exit(pytest.main(args=[__file__]))
