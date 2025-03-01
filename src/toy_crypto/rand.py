import math
import secrets
from bisect import bisect
from collections.abc import MutableSequence, Sequence
from itertools import accumulate, repeat
from typing import Any, Optional


def randrange(*args: int) -> int:
    """
    Like :py:func:`random.randrange`, but uses RNG from :py:mod:`secrets`.
    """

    if any([not isinstance(arg, int) for arg in args]):
        raise TypeError("arguments must be integers")

    start = 0
    step = 1
    match len(args):
        case 1:
            stop = args[0]
        case 2:
            start = args[0]
            stop = args[1]
        case 3:
            start = args[0]
            stop = args[1]
            step = args[2]

        case _:
            raise TypeError("Must have 1, 2, or 3 arguments")

    diff = stop - start
    if diff < 1:
        raise ValueError("stop must be greater than start")

    if step < 1:
        raise ValueError("step must be positive")

    if diff == 1:
        return start

    if step >= diff:  # only the bottom of the range will be allowed
        return start

    r = secrets.randbelow(diff // step)
    r *= step
    r += start

    return r


def shuffle(x: MutableSequence[Any]) -> None:
    """Like :py:func:`random.shuffle`, but uses RNG from :py:mod:`secrets`."""

    # Uses the "modern" Fisher-Yates shuffle from Knuth via
    # https://en.wikipedia.org/wiki/Fisher–Yates_shuffle#The_modern_algorithm

    n = len(x)
    if n < 2:
        return
    for i in range(n - 1):
        j = randrange(i, n)
        x[i], x[j] = x[j], x[i]


# from FullRandom example in
# https://docs.python.org/3/library/random.html#examples
def random() -> float:
    """returns a 32-bit float in [0.0, 1.0)"""

    mantissa = 0x10_0000_0000_0000 | secrets.randbits(52)
    exponent = -53
    x = 0
    while not x:
        x = secrets.randbits(32)
        exponent += x.bit_length() - 32
    return math.ldexp(mantissa, exponent)


def choices[T](
    population: Sequence[T],
    weights: Optional[Sequence[float]] = None,
    *,
    cum_weights: Optional[Sequence[float]] = None,
    k: int = 1,
) -> Sequence[T]:
    """Return a k sized list of population elements chosen with replacement.

    If the relative weights or cumulative weights are not specified,
    the selections are made with equal probability.

    This is the same as :py:func:`random.choices` except that it uses the
    the random number generator from :py:mod:1secrets`.
    Indeed, the implementation is just copied from that source.
    """

    # copied from https://github.com/python/cpython/blob/3.13/Lib/random.py#L458
    # except with static typing
    # and less abstract naming conventions for imported things
    n = len(population)
    if cum_weights is None:
        if weights is None:
            floor = math.floor
            return [population[floor(random() * n)] for i in repeat(None, k)]
        try:
            cum_weights = list(accumulate(weights))
        except TypeError:
            if not isinstance(weights, int):
                raise
            k = weights
            raise TypeError(
                f"The number of choices must be a keyword argument: {k=}"
            ) from None
    elif weights is not None:
        raise TypeError("Cannot specify both weights and cumulative weights")
    if len(cum_weights) != n:
        raise ValueError("The number of weights does not match the population")
    total = float(cum_weights[-1])
    if total <= 0.0:
        raise ValueError("Total of weights must be greater than zero")
    if not math.isfinite(total):
        raise ValueError("Total of weights must be finite")
    hi = n - 1
    return [
        population[bisect(cum_weights, random() * total, 0, hi)]
        for i in repeat(None, k)
    ]
