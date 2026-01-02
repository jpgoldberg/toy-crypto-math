"""
Helpful(?) type declarations and guards.

These are intended to make things easier for me, the author (jpgoldberg).
They are not carefully thought out.
This module is probably the least stable of any of these unstable modules.
"""

from dataclasses import dataclass
import math
from typing import (
    Annotated,
    Any,
    TypeGuard,
    Protocol,
    runtime_checkable,
)


# So that I can start playing with Annotated
@dataclass
class ValueRange:
    min: float
    max: float

    def within(self, x: float) -> bool:
        return self.min <= x <= self.max


@dataclass
class LengthRange:
    min: int
    max: int

    def within(self, length: int) -> bool:
        return self.min <= length <= self.max


Prob = Annotated[float, ValueRange(0.0, 1.0)]
"""Probability: A float between 0.0 and 1.0"""


def is_prob(val: Any) -> TypeGuard[Prob]:
    """true iff val is a float, s.t. 0.0 <= val <= 1.0"""
    if not isinstance(val, float):
        return False
    for datum in Prob.__metadata__:  # type: ignore[attr-defined]
        if isinstance(datum, ValueRange):
            if not datum.within(val):
                return False
    return True


PositiveInt = Annotated[int, ValueRange(1, math.inf)]
"""Positive integer."""


def is_positive_int(val: Any) -> bool:
    """true if val is a float, s.t. 0.0 <= val <= 1.0"""
    if not isinstance(val, int):
        return False
    for datum in PositiveInt.__metadata__:  # type: ignore[attr-defined]
        if isinstance(datum, ValueRange):
            if not datum.within(val):
                return False
    return True


Char = Annotated[str, LengthRange(1, 1)]
"""A string of length 1"""


def is_char(val: Any) -> bool:
    """true if val is a str of length 1"""
    if not isinstance(val, str):
        return False
    for datum in Char.__metadata__:  # type: ignore[attr-defined]
        if isinstance(datum, LengthRange):
            if not datum.within(len(val)):
                return False
    return True


Byte = Annotated[int, ValueRange(0, 255)]
"""And int representing a single byte."""


def is_byte(val: Any) -> bool:
    """True iff val is int s.t. 0 <= val < 256."""
    if not isinstance(val, int):
        return False
    for datum in PositiveInt.__metadata__:  # type: ignore[attr-defined]
        if isinstance(datum, ValueRange):
            if not datum.within(val):
                return False
    return True


@runtime_checkable
class SupportsBool(Protocol):
    def __bool__(self) -> bool: ...
