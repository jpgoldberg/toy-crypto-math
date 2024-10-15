"""Utility functions"""

import itertools
import math
from collections.abc import Iterator


def lsb_to_msb(n: int) -> Iterator[int]:
    """
    Iterator 0s and 1s representing bits of n, starting with the least significant bit.

    :raises TypeError: if n is not an integer.
    :raises ValueError: if n is negative.
    """
    if not isinstance(n, int):
        raise TypeError("n must be an integer")
    if n < 0:
        raise ValueError("n cannot be negative")

    while n > 0:
        yield n & 1
        n >>= 1


def digit_count(x: float, b: int = 10) -> int:
    """returns the number of digits (base b) in the integer part of x"""

    x = abs(x)
    result = math.floor(math.log(x, base=b) + 1)
    return result


def xor(m: bytes, pad: bytes) -> bytes:
    """Returns the xor of m with a (repeated) pad.

    The pad is repeated if it is shorter than m.
    This can be thought of as bytewise Vigenère
    """

    r: list[bytes] = [bytes([a ^ b]) for a, b in zip(m, itertools.cycle(pad))]

    return b"".join(r)
