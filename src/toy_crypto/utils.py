"""Utility functions"""

from collections.abc import Iterator
import itertools
from hashlib import blake2b
from base64 import a85encode
from typing import Optional, Self
from toy_crypto.types import Byte


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


class Xor:
    """Iterator that spits out xor of message with (repeated) pad.

    The iterator will run through successful bytes of message
    xor-ing those with successive bytes of pad, repeating
    pad if pad is shorter than message.

    Each iteration returns a non-negative int less than 256.
    """

    def __init__(
        self,
        message: Iterator[Byte] | bytes,
        pad: bytes,
    ) -> None:
        # Convert message to Iterator if needed
        self._message: Iterator[Byte] = iter(message)
        self._pad: Iterator[Byte] = itertools.cycle(pad)

    def __next__(self) -> Byte:
        b, p = next(zip(self._message, self._pad))
        return Byte(b ^ p)

    def __iter__(self: Self) -> Self:
        return self


def xor(message: bytes | Iterator[Byte], pad: bytes) -> bytes:
    """Returns the xor of message with a (repeated) pad.

    The pad is repeated if it is shorter than m.
    This can be thought of as bytewise Vigenère.
    """
    return bytes([b for b in Xor(message, pad)])


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


def hash_bytes(b: bytes) -> str:
    """Returns a python hashable from bytes.

    Primary intent is to have something that can be used
    as dictionary keys or members of sets.
    Collision resistance is the only security property
    that should be assumed here.

    The scheme may change from version to version
    """

    h = blake2b(b, digest_size=32).digest()
    t = str(a85encode(h))
    return t
