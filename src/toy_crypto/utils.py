"""Utility functions"""

from collections.abc import (
    Hashable,
    ItemsView,
    Iterator,
    KeysView,
    Mapping,
    Sequence,
)
import itertools
from hashlib import blake2b
from base64 import a85encode
import sys
from typing import Protocol, Self, ValuesView, runtime_checkable
import math
from toy_crypto.types import Byte


def digit_count(n: int, base: int = 10) -> int:
    """returns the number of digits (base b) of integer n.

    :raises ValueError: if base < 1
    """
    if base < 1:
        raise ValueError("base must be at least 1")

    n = abs(n)

    if base == 1:
        return n
    if base == 2:
        return n.bit_length()

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


class FrozenBidict[K: Hashable | int, V: Hashable]:
    """A bidirectional dictionary-like object.

    This is a very limited utility just for specific
    uses in this project. You will find more robust,
    flexible, and much more broadly applicable classes
    and functions in the outstanding
    `bidict library <https://bidict.readthedocs.io/en/main/>`__.
    """

    def __init__(self, s: Sequence[V] | Mapping[K, V]) -> None:
        """Create a map and its inverse.

        If s contains duplicate values, the behavior of the
        inverse map is undefined.
        """
        self._fwd: Mapping[K, V]
        self._inv: Mapping[V, K]
        if isinstance(s, Mapping):
            self._fwd = {k: v for k, v in s.items()}  # type: ignore[invalid-assignment]
        elif isinstance(s, Sequence):
            self._fwd = {k: v for k, v in enumerate(s)}  # type: ignore[misc]
        else:
            raise TypeError

        self._inv = {v: k for k, v in self._fwd.items()}

    def __getitem__(self, k: K) -> V:
        return self._fwd[k]

    def keys(self) -> KeysView[K]:
        return self._fwd.keys()

    def values(self) -> ValuesView[V]:
        return self._fwd.values()

    def items(self) -> ItemsView[K, V]:
        return self._fwd.items()

    def __len__(self) -> int:
        return len(self._fwd)

    def get(self, key: K, default: object = None) -> object:
        return self._fwd.get(key, default=default)

    @property
    def inverse(self) -> Mapping[V, K]:
        """The inverse map."""
        return self._inv


class Rsa129:
    """Text encoder/decoder used in RSA-129 challenge.

    Encoding scheme from Martin Gardner's 1977 article.
    """

    bimap: FrozenBidict[int, str] = FrozenBidict(" ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    @classmethod
    def encode(cls, text: str) -> int:
        """Encode text to number"""

        result = 0
        for c in text:
            result *= 100
            result += cls.bimap.inverse[c]
        return result

    @classmethod
    def decode(cls, number: int) -> str:
        """Decode number to text."""
        chars: list[str] = []
        while True:
            number, rem = divmod(number, 100)
            chars.append(cls.bimap[rem])
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


def next_power2(n: int) -> int:
    """Returns smallest *p* such that :math:`2^p \\geq n`.

    :raises ValueError: if n is less than 1.
    """

    if n < 1:
        raise ValueError("n must be positive")

    if n <= 2:
        return 1

    # I don't want to use log2 because the floating point approximation
    # might get this wrong for large values, so bit fiddling instead.

    # if n is a power of 2, then only its leading bit will be 1
    if not (n & (n - 1)):
        return n.bit_length() - 1

    p = 2  # we have covered the p = 1 cases
    t = 4
    while t < n:
        t *= 2
        p += 1
    return p


def nearest_multiple(n: int, factor: int, direction: str = "round") -> int:
    """Returns multiple of factor that is near ``n``.

    Given an input number, *n* and a factor *f* returns *m* such that

    - :math:`f|m` (*f* divides *n*);
    - :math:`\\left|n - m\\right| < f`
        (There is no multiples of *f* between *n* and *m*);

    As a consequence this always returns n if n is a multiple of factor.

    When *n* is not a multiple of factor,
    which of the two possible solutions to those conditions is returned
    depends on the value of of the ``direction`` parameter.

    :param n: The integer get a nearby multiple of factor of
    :param factor: The number that the returned values must be a multiple of.
    :param direction:
        Direction in which to round when n is not a multiple of factor

        "next"
            returns nearest multiple further from 0;

        "previous"
            returns nearest multiple toward 0;

        "round"
            returns nearest multiple and
            behaves like "previous" is if nearest multiples are
            equidistant from n

    :raises ValueError: if direction is not one of 'next', 'previous', 'round'.
    """

    factor = abs(factor)
    # special cases
    if factor == 0:
        return 0

    if factor == 1:
        return n

    if n == 0:
        return 0

    if n % factor == 0:
        return n

    # Now we have to deal with rounding and our three ways to do it
    sign = -1 if n < 0 else 1
    n = abs(n)

    q, r = divmod(n, factor)
    prev: int = int(q) * factor
    next: int = prev + factor

    match direction:
        case "previous":
            return sign * prev
        case "next":
            return sign * next
        case "round":
            if r > math.ceil(factor / 2) - 1:
                return sign * next
            return sign * prev
        case _:
            raise ValueError(f"Invalid direction: '{direction}'")


@runtime_checkable
class SuppprtsName(Protocol):
    """Objects with '__name__1'"""

    __name__: str


def export[F: SuppprtsName](fn: F) -> F:
    """Decorator to mark class or function as exported from module

    See https://brandonrozek.com/blog/exportpydecorator/
    """

    if isinstance(fn, SuppprtsName):
        name = fn.__name__
    else:
        raise TypeError("Please respect the type annotation")
    mod = sys.modules[fn.__module__]
    if hasattr(mod, "__all__"):
        mod.__all__.append(name)
    else:
        setattr(mod, "__all__", [name])
    return fn
