"""Utility functions"""

import itertools
from collections.abc import Iterator
from typing import Optional


def lsb_to_msb(n: int) -> Iterator[int]:
    """
    0s and 1s representing bits of n, starting with the least significant bit.

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


def digit_count(n: int, base: int = 10) -> int:
    """returns the number of digits (base b) of integer n.

    :raises ValueError: if base < 2
    :raises TypeError: if n is not an integer

    """

    if base < 2:
        raise ValueError("base must be at least 2")

    if not isinstance(n, int):
        raise TypeError("n must be an integer")

    n = abs(n)

    # Handling this case separately seems better than trying
    # to simulate a do-while in Python.
    if n == 0:
        return 1

    digits = 0
    while n > 0:
        digits += 1
        n = n // base
    return digits


def xor(m: bytes, pad: bytes) -> bytes:
    """Returns the xor of m with a (repeated) pad.

    The pad is repeated if it is shorter than m.
    This can be thought of as bytewise Vigenère
    """

    r: list[bytes] = [bytes([a ^ b]) for a, b in zip(m, itertools.cycle(pad))]

    return b"".join(r)


class Rsa129:
    """Text encoder/decoder used in RSA-129 challenge.

    Encoding scheme from Martin Gardner's 1977 article.
    """

    _abc: list[str] = list(" ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    _abc_index: Optional[dict[str, int]] = None

    @classmethod
    def _make_index(cls) -> dict[str, int]:
        if cls._abc_index is None:
            cls._abc_index = {c: i for i, c in enumerate(cls._abc)}
        return cls._abc_index

    def __init__(self) -> None:
        self._make_index()

    @classmethod
    def encode(cls, text: str) -> int:
        """Encode text"""

        indx = cls._make_index()
        result = 0
        for c in text:
            result *= 100
            result += indx[c]
        return result

    @classmethod
    def decode(cls, number: int) -> str:
        """Decode text."""
        chars: list[str] = []
        while True:
            number, rem = divmod(number, 100)
            chars.append(cls._abc[rem])
            if number == 0:
                break
        return "".join(reversed(chars))
