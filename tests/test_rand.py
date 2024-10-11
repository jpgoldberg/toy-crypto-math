import sys

import pytest
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

            counts[r] += 1

        assert all([c > 0 for c in counts.values()])


def test_random() -> None:
    trials = 1024
    for _ in range(trials):
        x = rand.random()
        assert x >= 0.0
        assert x < 1.0


# Slightly different invocations of mypy have very different opinions
@pytest.mark.statistical  # type: ignore[misc,unused-ignore]
def test_shuffle() -> None:
    trials = 2048

    input = ["A", "B", "C"]
    permutations = ["ABC", "ACB", "BAC", "BCA", "CAB", "CBA"]
    counts = {p: 0 for p in permutations}

    for _ in range(trials):
        # Note that shuffle shuffles in place
        c = input.copy()
        rand.shuffle(c)
        s = "".join(c)
        assert s in permutations
        counts[s] += 1

    mle = trials // len(permutations)
    # I should calculate the odds of test failure for good shuffle, but not now
    expected_floor = int(mle / 2)
    expected_ceiling = trials - expected_floor

    assert min(counts.values()) > expected_floor
    assert max(counts.values()) < expected_ceiling


if __name__ == "__main__":
    sys.exit(pytest.main(args=[__file__]))
