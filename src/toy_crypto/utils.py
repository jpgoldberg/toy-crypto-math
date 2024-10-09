from collections.abc import Generator, MutableSequence
import math
import secrets


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


def suffle(x: MutableSequence) -> MutableSequence:
    "Shuffles sequence in places using a Cryptographically Secure RNG."

    # Fisher-Yates Shuffle.
    # https://en.wikipedia.org/wiki/Fisher–Yates_shuffle

    n = len(x)
    for i in range(n - 2):
        j = secrets.randbelow(n - i) + i
        x[i], x[j] = x[j], x[i]

    return x
