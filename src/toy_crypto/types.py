"""
Helpful(?) type declarations and guards.

These are intended to make things easier for me, the author (jpgoldberg).
They are not carefully thought out.
This module is probably the least stable of any of these unstable modules.
"""

import math
import re
import sys  # for getrecursionlimit
import typing
from abc import ABC, abstractmethod
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import wraps
from typing import (
    Annotated,
    Any,
    Callable,
    NewType,
    Protocol,
    Sized,
    TypeAlias,
    TypeAliasType,
    TypeGuard,
    Union,
    cast,
    runtime_checkable,
)

import annotated_types
from annotated_types import (
    Interval as Interval,
)
from annotated_types import (
    Len,
    SupportsGe,
    SupportsGt,
    SupportsLe,
    SupportsLt,
    SupportsMod,
)

_RECURSION_LIMIT = sys.getrecursionlimit()


class AnnotatedType(ABC):
    __metadata__: tuple[Any]
    __origin__: type


# Used for function parameters for type or annotated types
TypeOrAType = type | Annotated[Any, ...]


def is_annotated_type(val: Any) -> TypeGuard[AnnotatedType]:
    return typing.get_origin(val) is Annotated


class _Constraint(ABC):
    """Abstract class that constraints must subclass."""

    @abstractmethod
    def is_valid(self, val: object) -> bool:
        """True iff val satisfies the constraint"""
        ...


Constraint = Union[
    annotated_types.BaseMetadata,
    "re.Pattern[bytes]",
    "re.Pattern[str]",
    slice,
]


def check_gt(constraint: Constraint, val: SupportsGt) -> bool:
    assert isinstance(constraint, annotated_types.Gt)
    return val > constraint.gt  # mypy: ignore[no-return-any]


def check_lt(constraint: Constraint, val: SupportsLt) -> bool:
    assert isinstance(constraint, annotated_types.Lt)
    return val < constraint.lt  # mypy: ignore[no-return-any]


def check_ge(constraint: Constraint, val: SupportsGe) -> bool:
    assert isinstance(constraint, annotated_types.Ge)
    return val >= constraint.ge  # mypy: ignore[no-return-any]


def check_le(constraint: Constraint, val: SupportsLe) -> bool:
    assert isinstance(constraint, annotated_types.Le)
    return val <= constraint.le  # mypy: ignore[no-return-any]


def check_multiple_of(constraint: Constraint, val: SupportsMod) -> bool:
    assert isinstance(constraint, annotated_types.MultipleOf)
    mult_of = constraint.multiple_of
    mult_of = cast(SupportsMod, mult_of)
    return val % mult_of == 0  # mypy: ignore[no-return-any]


def check_len(constraint: Constraint | slice, val: Any) -> bool:
    """Checks length of val against Len, MinLen, MaxLen, or slice."""

    # These are inclusive
    min_length: int
    max_length: int | None

    if isinstance(constraint, slice):
        min_length = constraint.start or 0
        max_length = constraint.stop
    else:
        min_length = getattr(constraint, "min_length", 0)
        max_length = getattr(constraint, "max_length", None)

    if len(val) < min_length:
        return False
    if max_length is not None and len(val) > max_length:
        return False
    return True


def check_predicate(constraint: Constraint, val: Any) -> bool:
    assert isinstance(constraint, annotated_types.Predicate)
    return constraint.func(val)


def check_timezone(constraint: Constraint, val: Any) -> bool:
    assert isinstance(constraint, annotated_types.Timezone)
    assert isinstance(val, datetime)
    if isinstance(constraint.tz, str):
        return val.tzinfo is not None and constraint.tz == val.tzname()
    elif isinstance(constraint.tz, timezone):
        return val.tzinfo is not None and val.tzinfo == constraint.tz
    elif constraint.tz is None:
        return val.tzinfo is None
    # ellipsis
    return val.tzinfo is not None


type Validator = Callable[[Constraint, Any], bool]

VALIDATORS: dict[type | slice, Validator] = {
    annotated_types.Gt: check_gt,
    annotated_types.Lt: check_lt,
    annotated_types.Ge: check_ge,
    annotated_types.Le: check_le,
    annotated_types.MultipleOf: check_multiple_of,
    annotated_types.Predicate: check_predicate,
    annotated_types.Len: check_len,
    annotated_types.MaxLen: check_len,
    annotated_types.MinLen: check_len,
    annotated_types.Timezone: check_timezone,
    slice: check_len,
}


class ValueRange[T: SupportsLe](_Constraint):
    """Constrain the values to a range."""

    def __init__(self, min: T | None, max: T | None) -> None:
        """Set minimum and maximum.

        Use `None` for no minimum or maximum
        """
        self._min: T | float = -math.inf if min is None else min
        self._max: T | float = math.inf if max is None else max

    @property
    def min(self) -> SupportsLe:
        return self._min

    @property
    def max(self) -> SupportsLe:
        return self._max

    def is_valid(self, val: object) -> bool:
        """True iff min <= val <= max.

        If val can't be compared to min or max
        errors will be passed upward.
        """
        return self._min <= val <= self._max  # type: ignore[operator]

    def __str__(self) -> str:
        return f"ValueRange({self._min}, {self._max})"


@dataclass
class LengthRange(_Constraint):
    """Constrain the length to a range."""

    def __init__(self, min: int | None, max: int | None) -> None:
        """Set minimum and maximum. These are inclusive.

        Use `None` for no minimum or maximum.
        """
        self._min: float = -math.inf if min is None else min
        self._max: float = math.inf if max is None else max

    def is_valid(self, val: object) -> bool:
        """True iff min <= len(val) <= max.

        :raises TypeError: if val is not Sized.
        """
        if not isinstance(val, Sized):
            raise TypeError("Must support len(val)")
        return self._min <= len(val) <= self._max

    @property
    def min(self) -> float:
        return self._min

    @property
    def max(self) -> float:
        return self._max

    def __str__(self) -> str:
        return f"LengthRange({self._min}, {self._max})"


def _predicate_description(
    base_type: type,
    constraints: Sequence[_Constraint | Constraint],
    param_name: str = "val",
) -> str:
    type_name = base_type.__name__

    intro = f"True if and only if {param_name} satisfies all of\n"
    conditions: list[str] = [f"is of type {type_name}"]
    conditions += [f"meets {c}" for c in constraints]

    text = "\n- ".join((intro, *conditions))

    return text


def _predicate_doc(
    tp: TypeOrAType,
    param_name: str = "value",
    prefix: str = "",
    suffix: str = "",
) -> str:
    """Generates docstring for predicates for annotated types."""

    if not is_annotated_type(tp):
        return f"True only if {param_name} is of {type(tp)}"

    # Now for annotated types
    origin = tp.__origin__
    origin_name = origin.__name__

    intro = f"True if and only if {param_name} satisfies all of\n"
    conditions: list[str] = [f"is of type {origin_name}"]
    conditions += [f"meets {c}" for c in get_constraints(tp)]

    text = prefix + "\n- ".join((intro, *conditions)) + suffix

    return text


_Predicate: TypeAlias = Callable[[Any], bool]
"""Type of (generated) predicates."""


def make_predicate(
    name: str,
    # t: NewType | AnnotatedType | type,
    t: object,
    constraints: Sequence[_Constraint] = tuple(),
    docstring: bool = True,
) -> _Predicate:
    """Create predicate from a type and constraints.

    :param name:
        The name that the predicate will know itself by in docstrings

    :param t:
        A type-like thing, including instances of
        ``type``,
        ``typing.TypeAliasType``,
        ``typing.Annotated`` types,
        and ``typing.NewType``.

    :param constraints:
        The :class:`Constraint`\\ s that the predicate should enforce.

    :param docstring:
        Create a docstring from the ``name`` and ``constraints`` for
        the created predicate

    If ``t`` is an Annotated type, any Constraints provided among its
    ``__metadata__`` will be included along with any constraints
    provided to this function.

    The order in which constraints are tested in the generated
    predicate is not defined.
    """

    cons = tuple(constraints)

    if is_annotated_type(t):
        base_type = t.__origin__
        cons += tuple(
            filter(lambda c: isinstance(c, _Constraint), t.__metadata__)
        )

    elif isinstance(t, NewType):
        # This relies on undocumented features of NewType
        # that I have gleaned from the source.
        st = t.__supertype__
        st_loop_count = 0  # Probably not needed, but I feel safer this way
        while not isinstance(st, type):
            if st_loop_count >= _RECURSION_LIMIT:
                raise Exception("NewTypes went too deep")
            st = st.__supertype__
            st_loop_count += 1
        base_type = st

    elif isinstance(t, TypeAliasType):
        tv = t.__value__
        tv_loop_count = 0
        while not isinstance(tv, type):
            if tv_loop_count >= _RECURSION_LIMIT:
                raise Exception("TypeAliases went too deep")
            tv = tv.__value
            tv_loop_count += 1
        base_type = tv

    elif isinstance(t, type):
        base_type = t
    else:
        raise TypeError("t must be the type of type we typically handle")

    def predicate(val: object) -> bool:
        if not isinstance(val, base_type):
            return False
        if not all((c.is_valid(val) for c in cons)):
            return False
        return True

    predicate.__name__ = name
    if docstring:
        predicate.__doc__ = _predicate_description(
            base_type=base_type, constraints=cons
        )
    return predicate


def document_pred(
    tp: TypeOrAType,
) -> Callable[[_Predicate], _Predicate]:
    """Decorator to add documentation for is_X where X is annotated type."""

    def decorator_doc(func: _Predicate) -> _Predicate:
        p_doc = _predicate_doc(tp)

        @wraps(func)
        def wrapper(value: Any) -> bool:
            return func(value)

        if func.__doc__ is None:
            wrapper.__doc__ = p_doc
        else:
            wrapper.__doc__ = func.__doc__ + "\n" + p_doc

        return wrapper

    return decorator_doc


# Prob = Annotated[float, ValueRange(0.0, 1.0)]
# Prob = NewType("Prob", float)


def get_constraints(tp: TypeOrAType) -> Iterator[Constraint]:
    # first get_args item is base type
    args = iter(typing.get_args(tp))
    next(args)
    for arg in args:
        if isinstance(arg, (annotated_types.BaseMetadata, re.Pattern, slice)):
            yield arg
        elif isinstance(arg, annotated_types.GroupedMetadata):
            yield from arg  # type: ignore


def is_valid(tp: TypeOrAType, value: Any) -> bool:
    """True iff all constraints on tp are true."""

    if not is_annotated_type(tp):
        return isinstance(tp, value)

    base_type = tp.__origin__
    if not isinstance(value, base_type):
        return False

    for constraint in get_constraints(tp):
        # if not VALIDATORS[type(constraint)](constraint, value):
        #    return False

        # Decomposed for debugging
        validator = VALIDATORS[type(constraint)]
        v = validator(constraint, value)
        if not v:
            return False

    return True


Prob = Annotated[float, Interval(ge=0.0, le=1.0)]


@document_pred(Prob)
def is_prob(value: Any) -> TypeGuard[Prob]:
    return is_valid(Prob, value)


PositiveInt = Annotated[int, annotated_types.Ge(1)]


@document_pred(PositiveInt)
def is_positive_int(val: Any) -> TypeGuard[PositiveInt]:
    return is_valid(PositiveInt, val)


Char = Annotated[str, Len(1, 1)]
"""A string of length 1"""


@document_pred(Char)
def is_char(val: Any) -> TypeGuard[Char]:
    return is_valid(Char, val)


Byte = Annotated[int, Interval(ge=0, le=255)]
"""And int representing a single byte."""


@document_pred(Byte)
def is_byte(val: Any) -> TypeGuard[Byte]:
    return is_valid(Byte, val)


@runtime_checkable
class SupportsBool(Protocol):
    """
    .. deprecated:: 0.6.2
       This never should have been a thing.
    """

    def __bool__(self) -> bool: ...
