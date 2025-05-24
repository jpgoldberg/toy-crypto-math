import sys

import pytest
from toy_crypto import bit_utils


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
        ba = bit_utils.PyBitArray(length, fill_bit=0)

        for idx in range(length):
            assert ba[idx] == 0

    def test_ones(self) -> None:
        length = 50
        ba = bit_utils.PyBitArray(length, fill_bit=1)

        for idx in range(length):
            assert ba[idx] == 1

    def test_set(self, sets: dict[str, set[int]]) -> None:
        universe = sets["universe"]
        size = len(universe)

        for name, test_set in sets.items():
            ba = bit_utils.PyBitArray(size, fill_bit=0)
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
            ba = bit_utils.PyBitArray(size, fill_bit=1)

            complement = universe - test_set
            for c in complement:
                ba[c] = 0

            for i in universe:
                if i in test_set:
                    assert ba[i] == 1, f"set: {name}; i: {i}"
                else:
                    assert ba[i] == 0, f"set: {name}; i: {i}"

    def test_to_int(self, sets: dict[str, set[int]]) -> None:
        p100_int = 159085582874019712269820766380
        primes100 = sets["primes"]
        size = len(sets["universe"])
        ba = bit_utils.PyBitArray(size, fill_bit=0)
        for p in primes100:
            ba[p] = 1
        result = int(ba)
        assert result == p100_int

    def test_from_int(self, sets: dict[str, set[int]]) -> None:
        p100_int = 159085582874019712269820766380
        primes100 = sets["primes"]
        ba = bit_utils.PyBitArray.from_int(p100_int)

        for idx, bit in enumerate(ba):
            if bit:
                assert idx in primes100
            else:
                assert idx not in primes100


class TestOtherBits:
    def bits(self) -> None:
        vectors = [
            (0b1101, [1, 0, 1, 1]),
            (1, [1]),
            (0, []),
            (0o644, [0, 0, 1, 0, 0, 1, 0, 1, 1]),
            (65537, [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]),
        ]
        for n, expected in vectors:
            bits = [bit for bit in bit_utils.bits(n)]
            assert bits == expected

    def test_hamming(self) -> None:
        s1 = b"this is a test"
        s2 = b"wokka wokka!!!"

        hd = bit_utils.hamming_distance(s1, s2)
        assert hd == 37


class TestIntBits:
    """Tests for the bit manipulation of ints"""

    vectors: list[tuple[int, tuple[int, bool], int]] = [
        (0, (0, True), 1),
        (1, (0, True), 1),
        (1, (0, False), 0),
        (5, (1, True), 7),
        (5, (3, True), 13),
        (16, (4, False), 0),
        (16, (4, True), 16),
        (15, (2, False), 11),
        (15, (3, False), 7),
    ]

    def test_set_true(self) -> None:
        for left, (bit, value), right in self.vectors:
            if not value:
                left, right = right, left
            result = bit_utils.set_bit(left, bit, True)
            assert result == right

    def test_set_false(self) -> None:
        for left, (bit, value), right in self.vectors:
            if value:
                # left, right = right, left
                continue
            result = bit_utils.set_bit(left, bit, False)
            assert result == right

    def test_get_bit(self) -> None:
        vectors: list[tuple[str, dict[int, int]]] = [
            ("10101100", {0: 0, 1: 0, 2: 1, 3: 1, 4: 0}),
        ]
        for s, d in vectors:
            n = int(s, 2)
            for idx, expected in d.items():
                b = bit_utils.get_bit(n, idx)
                assert b == expected

    def test_index_linerar(self) -> None:
        vectors: list[tuple[int | str, dict[int, int | None]]] = [
            ("11010", {1: 1, 2: 3, 3: 4, 4: None}),
            (
                0b100010100010100010101100,
                {1: 2, 2: 3, 3: 5, 4: 7, 5: 11, 6: 13, 7: 17, 8: 19, 9: 23},
            ),
        ]

        for n, d in vectors:
            if isinstance(n, str):
                n = int(n, 2)
            for k, expected in d.items():
                result = bit_utils.bit_index_linear(n, k, 1)
                assert result == expected

    def test_index(self) -> None:
        vectors: list[tuple[int | str, dict[int, int | None]]] = [
            (
                pow(2, 300) - 1,
                {b: b - 1 for b in range(1, 300, 17)},
            ),
            ("11010", {1: 1, 2: 3, 3: 4, 4: None}),
            (
                0b100010100010100010101100,
                {1: 2, 2: 3, 3: 5, 4: 7, 5: 11, 6: 13, 7: 17, 8: 19, 9: 23},
            ),
        ]

        for n, d in vectors:
            if isinstance(n, str):
                n = int(n, 2)
            for k, expected in d.items():
                result = bit_utils.bit_index(n, k, 1)
                assert result == expected


if __name__ == "__main__":
    sys.exit(pytest.main(args=[__file__]))
