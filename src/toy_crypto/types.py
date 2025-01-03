"""
Helpful(?) type declarations and guards.

These are intended to make things easier for me, the author (jpgoldberg).
They are not carefully thought out.
This module is probably the least stable of any of these unstable modules.
"""

from typing import Any, NewType, Optional, TypeGuard, Protocol

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
    """true if val is a float, s.t. 0.0 <= va <= 1.0"""
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
        try:
            return self._value == other.__bool__()  # type: ignore[no-any-return]
        except AttributeError:
            return NotImplemented
