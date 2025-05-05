"""
Helpful(?) type declarations and guards.

These are intended to make things easier for me, the author (jpgoldberg).
They are not carefully thought out.
This module is probably the least stable of any of these unstable modules.
"""

from typing import (
    Any,
    Callable,
    NewType,
    Optional,
    Self,
    TypeGuard,
    Protocol,
    Union,
    runtime_checkable,
)

import operator

Prob = NewType("Prob", float)
"""Probability: A float between 0.0 and 1.0"""


def is_prob(val: Any) -> TypeGuard[Prob]:
    """true if val is a float, s.t. 0.0 <= va <= 1.0"""
    if not isinstance(val, float):
        return False
    return val >= 0.0 and val <= 1.0


PositiveInt = NewType("PositiveInt", int)
"""Positive integer."""


def is_positive_int(val: Any) -> TypeGuard[PositiveInt]:
    """true if val is a float, s.t. 0.0 <= val <= 1.0"""
    if not isinstance(val, int):
        return False
    return val >= 1


Byte = int
"""And int representing a single byte.

Currently implemented as a type alias.
As a consequence, type checking is not going to identify
cases where an int out of the range of a byte is used.
"""


def is_byte(val: Any) -> bool:
    """True iff val is int s.t. 0 <= val < 256."""
    if not isinstance(val, int):
        return False
    return 0 <= val and val < 256


@runtime_checkable
class SupportsBool(Protocol):
    def __bool__(self) -> bool: ...


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
        return self._value

    def as_bool(self) -> bool:
        return self._value

    def as_int(self) -> int:
        if not self._as_int:
            self._as_int = 1 if self._value else 0
        return self._as_int

    def as_bytes(self) -> bytes:
        if not self._as_bytes:
            self._as_bytes = (
                (1).to_bytes(1, "big")
                if self._value
                else (0).to_bytes(1, "big")
            )
        return self._as_bytes

    def __eq__(self, other: Any) -> bool:
        ob = self._other_bool(other)
        if ob is None:
            return NotImplemented
        ob = other.__bool__()

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
        sb = self.as_bool()
        tvalue = expr(sb, other)

        if isinstance(other, Bit):
            return Bit(tvalue)

        if isinstance(other, int):
            return 1 if tvalue else 0
        if isinstance(other, bytes):
            return (1).to_bytes(1, "big") if tvalue else (0).to_bytes(1, "big")

        return tvalue

    def __and__(self, other: Any) -> Union["Bit", int, bool, bytes]:
        ob = self._other_bool(other)
        if ob is None:
            return NotImplemented

        return self._logic(other=ob, expr=lambda s, o: s and o)

    def __xor__(self, other: Any) -> Union["Bit", int, bool, bytes]:
        ob = self._other_bool(other)
        if ob is None:
            return NotImplemented

        return self._logic(other=ob, expr=lambda s, o: operator.xor(s, o))

    def __or__(self, other: Any) -> Union["Bit", int, bool, bytes]:
        ob = self._other_bool(other)
        if ob is None:
            return NotImplemented

        return self._logic(other=ob, expr=lambda s, o: s or o)

    def inv(self) -> "Bit":
        inv_b = not self.as_bool()
        return Bit(inv_b)

    def __inv__(self) -> "Bit":
        return self.inv()


class PyBitArray:
    """A pure Python bitarray-like object.

    This does not implement all methods of bitarray,
    nor does it fully follow the bitarray API.
    """

    """
    Internal little-endian bytearray of big endian bytes,
    but that shouldn't be seen by users.

    So the bit at index 0 will be the right-most bit of the left-most byte.
    If I do this right, users will never have to know or deal with that.
    """

    @staticmethod
    def _inv8(n: int) -> int:
        return (-n) % 8

    @staticmethod
    def _flip_end(byte: int) -> int:
        if byte < 0 or byte > 255:
            raise ValueError("byte is not representable as byte")
        result = 0
        for p in range(8):
            byte, b = divmod(byte, 2)
            result += b * (2 ** (8 - p))
        return result

    def __init__(self, bit_length: int, fill_bit: int = 0) -> None:
        if isinstance(bit_length, int):
            if bit_length < 0:
                raise ValueError("bit_length cannot be negative")

            fill_byte: int
            match fill_bit:
                case 0:
                    fill_byte = 0
                case 1:
                    fill_byte = 255
                case _:
                    raise ValueError("fill_bit must be 0 or 1")

            self._length = bit_length
            byte_len, self._remainder = divmod(self._length, 8)
            if self._remainder > 0:
                byte_len += 1
            self._data = bytearray([fill_byte] * byte_len)
            self._data[-1] >>= self._remainder

        # elif:  # Other types will be added later. Perhaps
        else:
            raise NotImplementedError(
                f"Not implemented for {type(bit_length)}"
            )

    def __getitem__(self, index: int) -> int:
        byte_index, remainder = divmod(index, 8)
        bit_index = self._inv8(remainder)
        byte = self._data[byte_index]
        value = byte & 1 << bit_index
        return 1 if value != 0 else 0

    def __setitem__(self, index: int, value: int) -> None:
        byte_index, remainder = divmod(index, 8)
        bit_index = self._inv8(remainder)
        byte = self._data[byte_index]

        mask: int
        match value:
            case 0:
                mask = ~(1 << bit_index)

            case 1:
                mask = 1 << bit_index

            case _:
                raise ValueError("Value must be 1 or 0")
        byte |= mask
        self._data[byte_index] = byte

    def byte_len(self) -> int:
        """Length in bytes"""
        return len(self._data)

    def __len__(self) -> int:
        return self._length

    @classmethod
    def from_bytes(cls, byte_data: bytes, endian: str = "big") -> Self:
        if endian not in ["big", "little"]:
            raise ValueError('endian must be "big" or "little"')

        ints: list[int] = [int(b) for b in byte_data]

        result = super().__new__(cls)

        if endian == "big":
            result._data = bytearray(ints)
        else:
            result._data = bytearray(ints[::-1])
        result._length = 8 * len(result._data)

        return result

    def to_bytes(self, endian: str = "big") -> bytes:
        if endian not in ["big", "little"]:
            raise ValueError('endian must be "big" or "little"')

        if endian == "big":
            return bytes(self._data)
        return bytes(self._data[::-1])
