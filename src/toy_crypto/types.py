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
    Callable,
    Sized,
    Protocol,
    runtime_checkable,
)


@runtime_checkable
class AnnotatedType(Protocol):
    __metadata__: tuple[Any]
    __origin__: type


@dataclass
class ValueRange:
    min: float
    max: float

    def is_ok(self, x: float) -> bool:
        return self.min <= x <= self.max


@dataclass
class LengthRange:
    min: int
    max: int

    def is_ok(self, val: object) -> bool:
        # Unsized things automatically pass
        if not isinstance(val, Sized):
            return True
        return self.min <= len(val) <= self.max


type Predicate = Callable[[object], bool]


def make_predicate(t: type | AnnotatedType) -> Predicate:
    def predicate(val: object) -> bool:
        if not isinstance(t, AnnotatedType):
            return isinstance(val, t)

        # It is an Annotated type
        if not isinstance(val, t.__origin__):
            return False
        for datum in t.__metadata__:
            if isinstance(datum, ValueRange):
                assert isinstance(val, float | int)
                if not datum.is_ok(val):
                    return False
            elif isinstance(datum, LengthRange):
                if not datum.is_ok(val):
                    return False
        return True

    return predicate


Prob = Annotated[float, ValueRange(0.0, 1.0)]
"""Probability: A float between 0.0 and 1.0"""

assert isinstance(Prob, AnnotatedType)
is_prob: Predicate = make_predicate(Prob)

PositiveInt = Annotated[int, ValueRange(1, math.inf)]
"""Positive integer."""

assert isinstance(PositiveInt, AnnotatedType)
is_positive_int = make_predicate(PositiveInt)


Char = Annotated[str, LengthRange(1, 1)]
"""A string of length 1"""

assert isinstance(Char, AnnotatedType)
is_char = make_predicate(Char)


Byte = Annotated[int, ValueRange(0, 255)]
"""And int representing a single byte."""

assert isinstance(Byte, AnnotatedType)
is_byte = make_predicate(Byte)


@runtime_checkable
class SupportsBool(Protocol):
    def __bool__(self) -> bool: ...
