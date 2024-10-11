import itertools
import math
from collections.abc import Generator


def lsb_to_msb(n: int) -> Generator[int, None, None]:
    """
    Returns a generator of bits of n, starting from the least significant bit.
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
    """

    r: list[bytes] = [bytes([a ^ b]) for a, b in zip(m, itertools.cycle(pad))]

    return b"".join(r)
