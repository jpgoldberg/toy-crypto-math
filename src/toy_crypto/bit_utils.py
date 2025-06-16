"""
Various utilities for manipulationg bit-like things.

The utilities here are most subject to change
as many where just quick things I needed.
This is more of a trash heap than a well-thought-out module.
"""

from typing import Optional, Any, Union, Callable, Self
from collections.abc import Iterator
import operator
from .utils import xor
from .types import SupportsBool


def bits(n: int) -> Iterator[int]:
    """
    0s and 1s representing bits of n, starting with the least significant bit.

    :raises ValueError: if n is negative.
    """

    n = int(n)
    if n < 0:
        raise ValueError("n cannot be negative")

    while n > 0:
        yield n & 1
        n >>= 1


def get_bit(n: int, k: int) -> int:
    """returns k-th bit of n."""

    if k < 0:
        raise ValueError("k cannot be negative")
    return (n & (1 << (k))) >> (k)


def set_bit(n: int, k: int, value: bool | int = True) -> int:
    """Returns copy of n with k-th bit set to value."""

    # k must be greater than 0
    if k < 0:
        raise ValueError("k cannot be negative")

    if not value:
        # setting to 0
        return n & ~(1 << k)

    return (1 << k) | n


def bit_index_linear(n: int, k: int, b: bool | int = 1) -> int | None:
    """Returns which bit is the k-th b bit in n.

    This is to mimic bitarray.utils.count_n, but for working with python
    built-in int
    """

    if k < 1:
        raise ValueError("n must be positive")

    bc = n.bit_count() if b else (~n).bit_count()

    if k > bc:
        return None
    b = 1 if b else 0

    # naive code that just does a linear search count through bits of n
    count = 0
    for i in range(n.bit_length()):
        n, r = divmod(n, 2)
        if r == b:
            count += 1
            if count >= k:
                return i
    return None  # This really shouldn't ever be reached.


def bit_index(n: int, k: int, b: bool | int = 1) -> int | None:
    """Returns which bit is the k-th b bit in n.

    This is to mimic bitarray.utils.count_n, but for working with python
    built-in int
    """

    if k < 1:
        raise ValueError("k must be positive")

    bc = n.bit_count() if b else (~n).bit_count()
    bl = n.bit_length()

    if k > bc:
        return None
    b = 1 if b else 0

    linear_theshold = 31
    if bc <= linear_theshold:
        return bit_index_linear(n, k, b)

    mid_index = bl // 2
    midpoint = int(2**mid_index)
    upper, lower = divmod(n, midpoint)

    # Debugging check against alternative way to compute upper and lower
    assert upper == n >> mid_index
    assert lower == n & ((1 << mid_index) - 1)

    bcl = lower.bit_count()
    if bcl == k:
        return mid_index - 1
    if bcl > k:
        ret_val = bit_index(lower, k, b)
        return ret_val

    u_count = bit_index(upper, k - bcl, b)
    if u_count is not None:
        return bcl + u_count

    return None


class Bit:
    """
    Because I made poor choices earlier of how to represent
    bits, I need an abstraction.
    """

    def __init__(self, b: SupportsBool) -> None:
        self._value: bool = b is True
        self._as_int: Optional[int] = None
        self._as_bytes: Optional[bytes] = None

    def __bool__(self) -> bool:
        """Every Bit should be Truthy."""
        return self._value

    def as_int(self) -> int:
        """Returns 0 or 1."""
        if not self._as_int:
            self._as_int = 1 if self._value else 0
        return self._as_int

    def as_bytes(self) -> bytes:
        """Returns a big-endian byte. Either 0x00 or 0x01."""
        if not self._as_bytes:
            self._as_bytes = (
                (1).to_bytes(1, "big")
                if self._value
                else (0).to_bytes(1, "big")
            )
        return self._as_bytes

    def __eq__(self, other: Any) -> bool:
        """Equality with other."""
        ob = self._other_bool(other)
        if ob is None:
            return NotImplemented
        ob = bool(other)

        return self._value == ob

    @staticmethod
    def _other_bool(other: Any) -> Optional[bool]:
        if isinstance(other, bytes):
            ob = any([b != 0 for b in other])
        elif not isinstance(other, SupportsBool):
            return None
        else:
            ob = other.__bool__()
        return ob

    def _logic(
        self, other: bool, expr: Callable[[bool, bool], bool]
    ) -> Union["Bit", int, bool, bytes]:
        """
        Abstraction to manage type of :data:`other`
        for things like :func:`__and__` and :func:`__or__`.
        """
        sb = bool(self)
        tvalue = expr(sb, other)

        if isinstance(other, Bit):
            return Bit(tvalue)

        if isinstance(other, int):
            return 1 if tvalue else 0
        if isinstance(other, bytes):
            return (1).to_bytes(1, "big") if tvalue else (0).to_bytes(1, "big")

        return tvalue

    def __and__(self, other: Any) -> Union["Bit", int, bool, bytes]:
        """For the "&" operator."""
        ob = self._other_bool(other)
        if ob is None:
            return NotImplemented

        return self._logic(other=ob, expr=lambda s, o: s and o)

    def __xor__(self, other: Any) -> Union["Bit", int, bool, bytes]:
        """For the "^" operator."""
        ob = self._other_bool(other)
        if ob is None:
            return NotImplemented

        return self._logic(other=ob, expr=lambda s, o: operator.xor(s, o))

    def __or__(self, other: Any) -> Union["Bit", int, bool, bytes]:
        """For the "|" operator."""
        ob = self._other_bool(other)
        if ob is None:
            return NotImplemented

        return self._logic(other=ob, expr=lambda s, o: s or o)

    def inv(self) -> "Bit":
        inv_b = not self
        return Bit(inv_b)

    def __inv__(self) -> "Bit":
        return self.inv()


def set_bit_in_byte(byte: int, bit: int, value: SupportsBool) -> int:
    """Sets the bit-most significant bit to value in byte."""
    byte %= 256
    bit %= 8

    if value:
        byte |= 1 << bit
    else:
        byte &= ~(1 << bit)
    return byte % 256


def flip_end(byte: int) -> int:
    """Return int with reversed bit sequence"""
    if byte < 0 or byte > 255:
        raise ValueError("byte is not representable as byte")
    result = 0
    for p in range(8):
        byte, b = divmod(byte, 2)
        result += b * (2 ** (8 - p))
    return result


def hamming_distance(a: bytes, b: bytes) -> int:
    """Hamming distance between byte sequences of equal length.

    :raises ValueError: if len(a) != len(b).
    """

    if len(a) != len(b):
        raise ValueError("Lengths are unequal")

    # hamming distance will be the number of 1 bits in a xor b
    db: bytes = xor(a, b)
    # bit_count is only defined for ints, so
    return int.from_bytes(db, signed=False).bit_count()


class PyBitArray:
    """A pure Python bitarray-like object.

    This does not implement all methods of bitarray,
    nor does it fully follow the bitarray API.

    This is very much a work in progress.
    """

    """
    Internal little-endian bytearray of big endian bytes,
    but that shouldn't be seen by users.

    So the bit at index 0 will be the right-most bit of the left-most byte.
    If I do this right, users will never have to know or deal with that.
    """

    def __init__(self, bit_length: int, fill_bit: SupportsBool = 0) -> None:
        # Instance attributes that should always exist
        self._data: bytearray
        self._length: int  # length in used bits
        self._free_bits: int  # number of unused bits in last byte

        if bit_length < 0:
            raise ValueError("bit_length cannot be negative")

        fill_byte: int
        if not fill_bit:
            fill_byte = 0
        else:
            fill_byte = 255

        self._length = bit_length
        byte_len, self._free_bits = divmod(self._length, 8)
        if self._free_bits > 0:
            byte_len += 1
        self._data = bytearray([fill_byte] * byte_len)
        self._data[-1] >>= self._free_bits

    @classmethod
    def from_int(cls, n: int) -> Self:
        """New instance from int."""
        instance = cls(n.bit_length())

        idx = 0
        while n:
            n, r = divmod(n, 2)
            if r:
                instance[idx] = 1
            idx += 1

        return instance

    def append(self, b: SupportsBool) -> None:
        """appends bit b."""
        b = 1 if b else 0

        self._length += 1
        if self._free_bits == 0:
            self._data.append(b)
        else:
            self[-1] = b

        self._free_bits -= 1
        self._free_bits %= 8

    def _inner_getitem(self, index: int) -> int:
        while index < 0:
            index += self._length
        byte_index, bit_index = divmod(index, 8)
        byte = self._data[byte_index]
        value = byte & (1 << bit_index)
        return 1 if value != 0 else 0

    def __getitem__(self, index: int) -> int:
        """Retrieve a bit using [] notation."""
        if not index < self._length:
            raise IndexError
        return self._inner_getitem(index)

    def __setitem__(self, index: int, value: SupportsBool) -> None:
        """Set a bit using [] notation."""
        while index < 0:
            index += self._length

        byte_index, bit_index = divmod(index, 8)
        byte = self._data[byte_index]

        new_byte = set_bit_in_byte(byte, bit_index, value)
        self._data[byte_index] = new_byte

    @property
    def nbytes(self) -> int:
        """Length in bytes"""
        return len(self._data)

    @property
    def padbits(self) -> int:
        """Number of pad bits"""
        return self._free_bits

    def __len__(self) -> int:
        """len() is defined."""
        return self._length

    def bits(
        self, start: int = 0, stop: int | None = None, step: int = 1
    ) -> Iterator[int]:
        """Iterator of bits, from least significant."""
        if step == 0:
            raise ValueError("step cannot be 0")
        step_sign = 1 if step > 0 else -1

        match (stop, step_sign):
            case None, 1:
                stop = self._length
            case None, _:  # sign is negative
                stop = 0
            case _, _:
                stop = stop

        # I know this, you know this. Now the type checker will know this
        assert stop is not None
        indices = range(start, stop, step)

        for idx in indices:
            yield self[idx]

    def __iter__(self) -> Iterator[int]:
        return self.bits()

    def __int__(self) -> int:
        """Integer with first element as least significant bit"""
        return sum(b * (2**i) for i, b in enumerate(self))

    def count(self) -> int:
        """Returns number of 1 bits"""
        return int.from_bytes(self._data).bit_count()

    @classmethod
    def from_bytes(cls, byte_data: bytes, endian: str = "big") -> Self:
        ints: list[int]
        match endian.lower():
            case "big":
                ints = [int(b) for b in byte_data]
            case "little":
                ints = [int(b) for b in reversed(byte_data)]
            case _:
                raise ValueError('endian must be "big" or "little"')

        instance = cls(8 * len(ints))
        instance._data = bytearray(ints)

        return instance

    def to_bytes(self, endian: str = "big") -> bytes:
        if endian not in ["big", "little"]:
            raise ValueError('endian must be "big" or "little"')

        if endian == "big":
            return bytes(self._data)
        return bytes(self._data[::-1])

    def bit_index(self, k: int, b: int = 1) -> int | None:
        """The index of the n-th 1 or 0 bit."""

        # For the moment I will just use bit_index for int
        # TODO: Write b-search for bit index using native data
        as_int = int(self)
        return bit_index(as_int, k, b)
