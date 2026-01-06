"""
Helpful(?) type declarations and guards.

These are intended to make things easier for me, the author (jpgoldberg).
They are not carefully thought out.
This module is probably the least stable of any of these unstable modules.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
import math
from typing import (
    Annotated,
    Any,
    Callable,
    NewType,
    Sequence,
    Sized,
    TypeAlias,
    Protocol,
    TypeGuard,
    runtime_checkable,
)


@runtime_checkable
class AnnotatedType(Protocol):
    __metadata__: tuple[Any]
    __origin__: type


class Constraint(ABC):
    """Abstract class that constraints must subclass."""

    @abstractmethod
    def is_valid(self, val: object) -> bool:
        """True iff val satisfies the constraint"""
        ...


class ValueRange(Constraint):
    """Constrain the values to a range."""

    def __init__(self, min: float | None, max: float | None) -> None:
        """Set minimum and maximum.

        Use `None` for no minimum or maximum
        """
        self.min: float = -math.inf if min is None else min
        self.max: float = math.inf if max is None else max

    def is_valid(self, val: object) -> bool:
        """True iff min <= val <= max.

        If val can't be compared to float errors
        will be passed upward
        """
        return self.min <= val <= self.max  # type: ignore[operator]


@dataclass
class LengthRange(Constraint):
    """Constraint the length to a range."""

    def __init__(self, min: int | None, max: int | None) -> None:
        """Set minimum and maximum.

        Use `None` for no minimum or maximum.
        """
        self.min: float = -math.inf if min is None else min
        self.max: float = math.inf if max is None else max

    def is_valid(self, val: object) -> bool:
        """True iff min <= len(val) <= max.

        :raises TypeError: if val is not Sized.
        """
        if not isinstance(val, Sized):
            raise TypeError("Must support len(val)")
        return self.min <= len(val) <= self.max


Predicate: TypeAlias = Callable[[object], bool]
"""Type of (generated) predicates."""


def make_predicate(
    t: NewType | AnnotatedType | type,
    constraints: Sequence[Constraint] = tuple(),
) -> Predicate:
    """Create predicate from simple type or typing.Annotated.

    When given an Annotated type, the predicate
    checks for
    - base type
    - conformance to any :func:`ValueRange` annotations
    - conformance to any :func:`LengthRange` annotations

    .. caution::
       Current version ignores type parameters.
       That is ``tuple[str]`` will be treated as ``tuple``.
    """

    def predicate(val: object) -> bool:
        cons: tuple[Constraint, ...] = tuple(constraints)
        if isinstance(t, AnnotatedType):
            base_type = t.__origin__
            cons += tuple(t.__metadata__)

        elif isinstance(t, NewType):
            # This relies on undocumented features of NewType
            # that I have gleaned from the source.
            if not isinstance(t.__supertype__, type):
                raise TypeError("super-type is not so super after all")
            base_type = t.__supertype__

        elif isinstance(t, type):
            base_type = t

        if not isinstance(base_type, type):
            raise TypeError(
                "base type of type t is not the type of type"
                "we typically expect."
            )
        if not isinstance(val, base_type):
            return False
        for datum in cons:
            if isinstance(datum, Constraint):
                if not datum.is_valid(val):
                    return False
        return True

    return predicate


Prob = Annotated[float, ValueRange(0.0, 1.0)]
"""Probability: A float between 0.0 and 1.0"""

assert isinstance(Prob, AnnotatedType)
is_prob: Predicate = make_predicate(Prob)
"""True iff val is a float and 0.0 <= val <= 1.0"""

PositiveInt = Annotated[int, ValueRange(1, math.inf)]
"""Positive integer."""

assert isinstance(PositiveInt, AnnotatedType)
is_positive_int: Predicate = make_predicate(PositiveInt)
"""True iff val is an int and vat >= 1"""


Char = Annotated[str, LengthRange(1, 1)]
"""A string of length 1"""

assert isinstance(Char, AnnotatedType)
is_char: Predicate = make_predicate(Char)
"""True iff val is str and len(val) == 1"""


Byte = Annotated[int, ValueRange(0, 255)]
"""And int representing a single byte."""

assert isinstance(Byte, AnnotatedType)
is_byte: Predicate = make_predicate(Byte)


@runtime_checkable
class SupportsBool(Protocol):
    def __bool__(self) -> bool: ...


# Now experiment with a factory to subclass builtin


class Constrained(type):
    # class data
    _constraints: Sequence[Constraint]
    primary_base: type

    def __new__(
        cls, name: str, bases: tuple[type], attrs: dict[str, Any] = {}
    ):
        instance = super().__new__(cls, name, bases, attrs)
        return instance

    @classmethod
    def is_valid(cls, val: object) -> bool:
        if not isinstance(val, cls.primary_base):
            return False

        # I don't use "all" because this is easier to debug
        for c in cls._constraints:
            if not c.is_valid(val):
                return False
        return True


def make_subclass(
    name: str, base_type: type, constraints: Constraint | Sequence[Constraint]
) -> type[Constrained]:
    class SubClass(metaclass=Constrained):
        _constraints: Sequence[Constraint]
        if isinstance(constraints, Constraint):  # Not a sequence
            _constraints = (constraints,)
        else:
            _constraints = constraints

        _primary_base = base_type

        __name__ = name

        @classmethod
        def is_valid(cls, val: object) -> bool:
            if not isinstance(val, base_type):
                return False
            for c in cls._constraints:
                if not c.is_valid(val):
                    return False
            return True

        def __init__(self, value: object) -> None:
            if not self.is_valid(value):
                raise ValueError("Does not satisfy constraints")

    assert isinstance(SubClass, Constrained)
    return SubClass


Prob2 = make_subclass("Prob2", float, ValueRange(0.0, 1.0))


def is_prob2(value: object) -> TypeGuard[Prob2]:  # type: ignore
    return Prob2.is_valid(value)


def _dummy_function(x) -> Prob2:  # type: ignore
    if not is_prob2(x):
        raise ValueError
    return x


# Now let me try to copying bits of the NewType code
class NewConstrainedType:
    # the magic is in a C function _idfunc, but perhaps I
    # can that via NewType

    __call__ = NewType.__call__

    def __init__(
        self,
        name: str,
        tp: type,
        constraints: Constraint | Sequence[Constraint],
    ) -> None:
        self.__qualname__ = name
        if "." in name:
            name = name.rpartition(".")[-1]
        self.__name__ = name
        self.__supertype__ = tp

        self._constraints: Sequence[Constraint]
        if isinstance(constraints, Constraint):  # Not a sequence
            self._constraints = (constraints,)
        else:
            self._constraints = constraints

        # We don't do the module name thing from NewType

    def is_one_of_us(self, val: object) -> bool:
        if not isinstance(val, self.__supertype__):
            return False
        for c in self._constraints:
            if not c.is_valid(val):
                return False
        return True


# Prob3 = NewConstrainedType("Prob3", float, (ValueRange(0.0, 1.0),))
# Prob3 = cast(type[NewType], Prob3)
Prob3 = NewType("Prob3", float)


def is_prob3(val: object) -> TypeGuard[Prob3]:
    return Prob3.is_one_of_us(val)


def make_guard(
    name: str, tp: type[NewType], constraints: tuple[Constraint]
) -> object:
    def predicate(val: object):
        assert isinstance(tp.__supertype__, type)
        if not isinstance(val, tp.__supertype__):
            return False
        for c in constraints:
            if not c.is_valid(val):
                return False
        return True

    return predicate
