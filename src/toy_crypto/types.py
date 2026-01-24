"""
Helpful(?) type declarations and guards.

These are intended to make things easier for me, the author (jpgoldberg).
They are not carefully thought out.
This module is probably the least stable of any of these unstable modules.
"""

import sys  # for getrecursionlimit
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
    TypeAliasType,
    Protocol,
    TypeGuard,
    runtime_checkable,
)

_RECURSION_LIMIT = sys.getrecursionlimit()


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
        self._min: float = -math.inf if min is None else min
        self._max: float = math.inf if max is None else max

    @property
    def min(self) -> float:
        return self._min

    @property
    def max(self) -> float:
        return self._max

    def is_valid(self, val: object) -> bool:
        """True iff min <= val <= max.

        If val can't be compared to float errors
        will be passed upward
        """
        return self._min <= val <= self._max  # type: ignore[operator]

    def __str__(self) -> str:
        return f"ValueRange({self._min}, {self._max})"


@dataclass
class LengthRange(Constraint):
    """Constraint the length to a range."""

    def __init__(self, min: int | None, max: int | None) -> None:
        """Set minimum and maximum.

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
    base_type: type, constraints: Sequence[Constraint], param_name: str = "val"
) -> str:
    type_name = base_type.__name__

    intro = f"True if and only if {param_name} satisfies all of\n"
    conditions: list[str] = [f"is of type {type_name}"]
    conditions += [f"meets {c}" for c in constraints]

    text = "\n- ".join((intro, *conditions))

    return text


Predicate: TypeAlias = Callable[[object], bool]
"""Type of (generated) predicates."""


def make_predicate(
    name: str,
    # t: NewType | AnnotatedType | type,
    t: object,
    constraints: Sequence[Constraint] = tuple(),
    docstring: bool = True,
) -> Predicate:
    """Create predicate from a type and constraints.

    :param name:
        The name that the predicate will know itself by in docstrings
    :param t
        A type-like thing, including

        - instances of ``type`` (this includes most classes),
        - instances of ``typing.TypeAliasType`` (created in one of the many ways to create type aliases),
        - ``typing.Annotated`` types,
        - instances of ``typing.NewType``.

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
    if isinstance(t, AnnotatedType):
        base_type = t.__origin__
        cons += tuple(
            filter(lambda c: isinstance(c, Constraint), t.__metadata__)
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
                raise Exception("NewTypes went too deep")
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


# Prob = Annotated[float, ValueRange(0.0, 1.0)]
Prob = NewType("Prob", float)

# fmt: off
_is_prob: Predicate = make_predicate("is_prob", Prob, (ValueRange(0.0, 1.0),))
def is_prob(val: object) -> TypeGuard[Prob]:
    return _is_prob(val)
is_prob.__doc__ = _is_prob.__doc__
# fmt: on


# PositiveInt = Annotated[int, ValueRange(1, math.inf)]
type PositiveInt = int


is_positive_int: Predicate = make_predicate(
    "is_positive_int", PositiveInt, constraints=(ValueRange(1, math.inf),)
)


Char = Annotated[str, LengthRange(1, 1)]
"""A string of length 1"""

assert isinstance(Char, AnnotatedType)
is_char: Predicate = make_predicate("is_char", Char)
"""True iff val is str and len(val) == 1"""


Byte = Annotated[int, ValueRange(0, 255)]
"""And int representing a single byte."""

assert isinstance(Byte, AnnotatedType)
is_byte: Predicate = make_predicate("is_byte", Byte)


@runtime_checkable
class SupportsBool(Protocol):
    """
    .. deprecated:: 0.6.2
       This never should have been a thing.
    """

    def __bool__(self) -> bool: ...
