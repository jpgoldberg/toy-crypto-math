import pytest
import sys
from toy_crypto import rand


class TestRandRange:
    def test_range_even(self) -> None:
        expected_values = range(0, 10, 2)
        counts: dict[int, int] = {r: 0 for r in expected_values}
        for _ in range(1000):
            r = rand.randrange(0, 10, 2)
            assert r in expected_values

            counts[r] += 1

        # could run a more sophisticated statistical test, but
        # let's start with this
        assert all([c > 0 for c in counts.values()])

    def test_single_arg(self) -> None:
        top = 20
        trials = 200 * top
        counts: dict[int, int] = {r: 0 for r in range(top)}

        for _ in range(trials):
            r = rand.randrange(top)
            assert r >= 0
            assert r < top

            counts[r] +=1

        assert all([c > 0 for c in counts.values()])


if __name__ == "__main__":
    sys.exit(pytest.main(args=[__file__]))
