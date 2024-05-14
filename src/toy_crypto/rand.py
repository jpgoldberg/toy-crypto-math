"""Supplements Python secrets module"""

import secrets
from collections.abc import MutableSequence
from typing import Any


def randrange(*args: int) -> int:
    """Same as randmon.randrange(), but uses RNG from secrets."""

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
            raise TypeError("a more useful message should go here")

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
    """Shuffles x in place"""

    # Uses the "modern" Fisher-Yates shuffle from Knuth via
    # https://en.wikipedia.org/wiki/Fisher–Yates_shuffle#The_modern_algorithm

    n = len(x)
    if n < 2:
        return
    for i in range(n):
        j = randrange(i, n)
        x[i], x[j] = x[j], x[i]
