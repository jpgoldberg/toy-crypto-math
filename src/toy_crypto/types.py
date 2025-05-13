"""
Helpful(?) type declarations and guards.

These are intended to make things easier for me, the author (jpgoldberg).
They are not carefully thought out.
This module is probably the least stable of any of these unstable modules.
"""

from typing import (
    Any,
    NewType,
    TypeGuard,
    Protocol,
    runtime_checkable,
)


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
