from typing import Optional, Any, Union, Callable, Self
from collections.abc import Iterator
import operator
from .types import SupportsBool


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


def set_bit_in_byte(byte: int, bit: int, value: SupportsBool) -> int:
    byte %= 256
    bit %= 8

    if value:
        byte |= 1 << bit
    else:
        byte &= ~(1 << bit)
    return byte % 256


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
    def _flip_end(byte: int) -> int:
        if byte < 0 or byte > 255:
            raise ValueError("byte is not representable as byte")
        result = 0
        for p in range(8):
            byte, b = divmod(byte, 2)
            result += b * (2 ** (8 - p))
        return result

    def __init__(self, bit_length: int, fill_bit: SupportsBool = 0) -> None:
        # Instance attributes that should always exist
        self._data: bytearray
        self._length: int  #  length in used bits
        self._free_bits: int  # number of unused bits in last byte

        if isinstance(bit_length, int):
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

        # elif:  # Other types will be added later. Perhaps
        else:
            raise NotImplementedError(
                f"Not implemented for {type(bit_length)}"
            )

    def append(self, b: SupportsBool) -> None:
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
        if not index < self._length:
            raise IndexError
        return self._inner_getitem(index)

    def __setitem__(self, index: int, value: SupportsBool) -> None:
        while index < 0:
            index += self._length

        byte_index, bit_index = divmod(index, 8)
        byte = self._data[byte_index]

        new_byte = set_bit_in_byte(byte, bit_index, value)
        self._data[byte_index] = new_byte

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
