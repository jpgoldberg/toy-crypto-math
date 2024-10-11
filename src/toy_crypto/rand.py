"""Supplements Python secrets module"""

import math
import secrets
from collections.abc import MutableSequence
from typing import Any


def randrange(*args: int) -> int:
    """Same as random.randrange(), but uses RNG from secrets."""

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
    """Shuffles x in place using CSPRNG"""

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
