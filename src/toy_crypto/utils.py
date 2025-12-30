"""Utility functions"""

from collections.abc import (
    Hashable,
    ItemsView,
    Iterator,
    KeysView,
    Mapping,
    Sequence,
)
import itertools
from hashlib import blake2b
from base64 import a85encode
import sys
from typing import (
    Callable,
    Protocol,
    Self,
    ValuesView,
    cast,
    runtime_checkable,
)
import math
from toy_crypto.types import Byte

import logging

logging.getLogger(__name__)


def digit_count(n: int, base: int = 10) -> int:
    """returns the number of digits (base b) of integer n.

    :raises ValueError: if base < 1
    """
    if base < 1:
        raise ValueError("base must be at least 1")

    n = abs(n)

    if base == 1:
        return n
    if base == 2:
        return n.bit_length()

    if n == 0:
        return 1

    digits = 0
    while n > 0:
        digits += 1
        n = n // base
    return digits


class Xor:
    """Iterator that spits out xor of message with (repeated) pad.

    The iterator will run through successful bytes of message
    xor-ing those with successive bytes of pad, repeating
    pad if pad is shorter than message.

    Each iteration returns a non-negative int less than 256.
    """

    def __init__(
        self,
        message: Iterator[Byte] | bytes,
        pad: bytes,
    ) -> None:
        # Convert message to Iterator if needed
        self._message: Iterator[Byte] = iter(message)
        self._pad: Iterator[Byte] = itertools.cycle(pad)

    def __next__(self) -> Byte:
        b, p = next(zip(self._message, self._pad))
        return Byte(b ^ p)

    def __iter__(self: Self) -> Self:
        return self


def xor(message: bytes | Iterator[Byte], pad: bytes) -> bytes:
    """Returns the xor of message with a (repeated) pad.

    The pad is repeated if it is shorter than m.
    This can be thought of as bytewise Vigenère.
    """
    return bytes([b for b in Xor(message, pad)])


class FrozenBidict[K: Hashable | int, V: Hashable]:
    """A bidirectional dictionary-like object.

    This is a very limited utility just for specific
    uses in this project. You will find more robust,
    flexible, and much more broadly applicable classes
    and functions in the outstanding
    `bidict library <https://bidict.readthedocs.io/en/main/>`__.

    .. versionadded::0.6
    """

    def __init__(self, s: Sequence[V] | Mapping[K, V]) -> None:
        """Create a map and its inverse.

        If s contains duplicate values, the behavior of the
        inverse map is undefined.
        """
        self._fwd: Mapping[K, V]
        self._inv: Mapping[V, K]
        if isinstance(s, Mapping):
            self._fwd = {k: v for k, v in s.items()}  # type: ignore[invalid-assignment]
        elif isinstance(s, Sequence):
            self._fwd = {k: v for k, v in enumerate(s)}  # type: ignore[misc]
        else:
            raise TypeError

        self._inv = {v: k for k, v in self._fwd.items()}

    def __getitem__(self, k: K) -> V:
        return self._fwd[k]

    def keys(self) -> KeysView[K]:
        return self._fwd.keys()

    def values(self) -> ValuesView[V]:
        return self._fwd.values()

    def items(self) -> ItemsView[K, V]:
        return self._fwd.items()

    def __len__(self) -> int:
        return len(self._fwd)

    def get(self, key: K, default: object = None) -> object:
        return self._fwd.get(key, default=default)

    @property
    def inverse(self) -> Mapping[V, K]:
        """The inverse map."""
        return self._inv


class Rsa129:
    """Text encoder/decoder used in RSA-129 challenge.

    Encoding scheme from Martin Gardner's 1977 article.
    """

    bimap: FrozenBidict[int, str] = FrozenBidict(" ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    @classmethod
    def encode(cls, text: str) -> int:
        """Encode text to number"""

        result = 0
        for c in text:
            result *= 100
            result += cls.bimap.inverse[c]
        return result

    @classmethod
    def decode(cls, number: int) -> str:
        """Decode number to text."""
        chars: list[str] = []
        while True:
            number, rem = divmod(number, 100)
            chars.append(cls.bimap[rem])
            if number == 0:
                break
        return "".join(reversed(chars))


def hash_bytes(b: bytes) -> str:
    """Returns a python hashable from bytes.

    Primary intent is to have something that can be used
    as dictionary keys or members of sets.
    Collision resistance is the only security property
    that should be assumed here.

    The scheme may change from version to version
    """

    h = blake2b(b, digest_size=32).digest()
    t = str(a85encode(h))
    return t


def next_power2(n: int) -> int:
    """Returns smallest *p* such that :math:`2^p \\geq n`.

    :raises ValueError: if n is less than 1.
    """

    if n < 1:
        raise ValueError("n must be positive")

    if n <= 2:
        return 1

    # I don't want to use log2 because the floating point approximation
    # might get this wrong for large values, so bit fiddling instead.

    # if n is a power of 2, then only its leading bit will be 1
    if not (n & (n - 1)):
        return n.bit_length() - 1

    p = 2  # we have covered the p = 1 cases
    t = 4
    while t < n:
        t *= 2
        p += 1
    return p


def nearest_multiple(n: int, factor: int, direction: str = "round") -> int:
    """Returns multiple of factor that is near ``n``.

    Given an input number, *n* and a factor *f* returns *m* such that

    - :math:`f|m` (*f* divides *n*);
    - :math:`\\left|n - m\\right| < f`
        (There is no multiples of *f* between *n* and *m*);

    As a consequence this always returns n if n is a multiple of factor.

    When *n* is not a multiple of factor,
    which of the two possible solutions to those conditions is returned
    depends on the value of of the ``direction`` parameter.

    :param n: The integer get a nearby multiple of factor of
    :param factor: The number that the returned values must be a multiple of.
    :param direction:
        Direction in which to round when n is not a multiple of factor

        "next"
            returns nearest multiple further from 0;

        "previous"
            returns nearest multiple toward 0;

        "round"
            returns nearest multiple and
            behaves like "previous" is if nearest multiples are
            equidistant from n

    :raises ValueError: if direction is not one of 'next', 'previous', 'round'.
    """

    factor = abs(factor)
    # special cases
    if factor == 0:
        return 0

    if factor == 1:
        return n

    if n == 0:
        return 0

    if n % factor == 0:
        return n

    # Now we have to deal with rounding and our three ways to do it
    sign = -1 if n < 0 else 1
    n = abs(n)

    q, r = divmod(n, factor)
    prev: int = int(q) * factor
    next: int = prev + factor

    match direction:
        case "previous":
            return sign * prev
        case "next":
            return sign * next
        case "round":
            if r > math.ceil(factor / 2) - 1:
                return sign * next
            return sign * prev
        case _:
            raise ValueError(f"Invalid direction: '{direction}'")


@runtime_checkable
class SuppprtsName(Protocol):
    """Objects with '__name__1'"""

    __name__: str


def export[F: SuppprtsName](fn: F) -> F:
    """Decorator to mark class or function as exported from module

    See https://brandonrozek.com/blog/exportpydecorator/
    """

    if isinstance(fn, SuppprtsName):
        name = fn.__name__
    else:
        raise TypeError("Please respect the type annotation")
    mod = sys.modules[fn.__module__]
    if hasattr(mod, "__all__"):
        mod.__all__.append(name)
    else:
        setattr(mod, "__all__", [name])
    return fn


class _Point:
    """This is only used in find_zero."""

    function: Callable[[int], float] | None = None

    @classmethod
    def set_function(cls, f: Callable[[int], float]) -> None:
        cls.function = f

    def __init__(self, n: int, y: float) -> None:
        self._n = n

        # We only ever make use of the sign of x,
        # but let's keep this if we want to move to smarter
        # interpolation.
        self._y = y
        self._sign: int = 0 if self._y == 0 else 1 if self._y > 0 else -1

    @classmethod
    def from_n(cls, n: int) -> "_Point":
        if cls.function is None:
            raise Exception("function has not been defined")
        return _Point(n, cls.function(n))

    @property
    def y(self) -> float:
        return self._y

    @property
    def n(self) -> int:
        return self._n

    @property
    def sign(self) -> int:
        return self._sign

    def isclose(self, other: "_Point") -> bool:
        # if same point or adjacent
        return abs(self.n - other.n) < 2

    def linear_zero(self, other: "_Point") -> int:
        """Assuming points on straight line, zero.

        Abnormal: Do not use
        """
        if self.n == other.n:
            raise ValueError("Must be distinct points")
        if self.y == other.y:
            # A more general function would return None
            raise ValueError("line is horizontal")

        # US high school notation for slope/intercept form
        # y = mx + b
        # The linear zero should be near -b
        m: float = (self.y - other.y) / (self.n - other.n)
        b = self.y - m * self.n
        return -round(b)


@export
def find_zero(
    function: Callable[[int], float],
    initial_estimate: int = 0,
    initial_step: int = 256,
    max_iterations: int = 500,
    lower_bound: int | None = None,
    upper_bound: int | None = None,
) -> int:
    """Finds (nearly) smallest n for f(x) such that f(n) > 0.

    Performs a binary search for +0 of a non-decreasing function,
    :math:`f(n)`, to return an :math:`n_0` such that
    :math:`f(n_0) \\geq 0 \\land f(n_0 - 1) < 0`.

    :param function:
        The function for which you want to find the zero.
        Must be non-decreasing.
    :param initial_estimate:
        The closer this is to the actual zero,
        the less the computer will need to work to find it.
    :param initial_step:
        The initial step size.
    :param max_iterations:
        The number of times this will compute the function
        before it just gives you its best estimate that that
        time.
    :param lower_bound:
        Smallest meaningful *n* in f(n).
        If ``None``, treated as ``-math.inf``.
    :param upper_bound:
        Largest meaningful *n* in f(n).
        If ``None``, treated as ``math.inf``.

    :raises ValueError: if ``initial_step`` isn't positive.
    :raises ValueError: if not lower_bound <= initial_estimate <= upper_bound.

    .. warning::
        Results are undefined if function is not non-decreasing
        or if function isn't defined for every n in [lower_bound, upper_bound].

    .. caution::
        If f(n) is close to flat around n\\ :sub:`0` and
        n\\ :sub:`0` is large
        then the result may be approximate.

    .. caution::
        This has only been tested for use in
        :func:`toy_crypto.birthday.quantile`.

    .. versionadded:: 0.6
    """
    if initial_step < 1:
        raise ValueError("initial step size must be positive")

    if lower_bound is None:
        lower_bound = cast(int, -math.inf)

    if upper_bound is None:
        upper_bound = cast(int, math.inf)

    if not lower_bound <= initial_estimate < upper_bound:
        raise ValueError("Bounds and initial_estimate don't make sense")

    # We need to keep track of how many times function is called
    # so that we can enforce max_iterations (and log the information)
    call_count = 0

    def fun_wrapper(n: int) -> float:
        """Wrapper for function, tracking number of times called."""
        nonlocal call_count
        nonlocal function

        call_count += 1
        return function(n)

    # Set the poorly named _Point class to use our wrapped
    # function when creating points with .from_n()
    _Point.set_function(fun_wrapper)

    # We need to handle cases of
    # - f(lower_bound) >= 0
    # - f(upper_bound) <= 0
    # early, so rest of code can assume working bounds
    if upper_bound != math.inf:
        lowest_above = _Point.from_n(upper_bound)
        if lowest_above.sign != 1:
            return upper_bound
    else:
        lowest_above = _Point(upper_bound, math.inf)

    if lower_bound != -math.inf:
        highest_below = _Point.from_n(lower_bound)
        if highest_below.sign != -1:
            return lower_bound
    else:
        highest_below = _Point(lower_bound, -math.inf)

    start = _Point(initial_estimate, function(initial_estimate))
    match start.sign:
        case 0:
            return initial_estimate
        case 1:
            lowest_above = start
        case -1:
            highest_below = start

    # We need to first scale up to a step size that surrounds the zero
    step = (-1) * start.sign * initial_step
    previous = start

    # We will double the step size until we cross zero
    new_point = _Point.from_n(previous.n + step)
    while new_point.sign == previous.sign:
        match new_point.sign:
            case 0:
                return new_point.n
            case 1:
                lowest_above = new_point
            case -1:
                highest_below = new_point
        step *= 2
        previous = new_point

        next_n = new_point.n + step
        # This assumes we've already handled pathological bound cases
        next_n = min(upper_bound, max(lower_bound, next_n))
        new_point = _Point.from_n(next_n)

    # because python doesn't have a do while, we do this 1 more time
    # when the sign has changed
    match new_point.sign:
        case 0:
            return new_point.n
        case 1:
            lowest_above = new_point
        case -1:
            highest_below = new_point

    logging.info(
        f"zero in ({highest_below.n}, {lowest_above.n} "
        f"after {call_count} calls to function."
    )

    # At this point we have `new_point` and `previous` with opposite signs
    # The logic below is that best_other and new_point will always have
    # opposite signs (except for when new_point is at zero)
    # So we are ready for the bisection part
    best_other = previous
    while call_count < max_iterations and not (
        new_point.sign == 0 or new_point.isclose(best_other)
    ):
        best_other = highest_below if new_point.sign > 0 else lowest_above

        # Pick halfway n.
        # Linear interpolation runs into big enough
        # precision errors with the quantile function
        # that it is worse than useless.
        new_n = (best_other.n + new_point.n) // 2
        new_point = _Point.from_n(new_n)
        if new_point.sign < 0:
            highest_below = new_point
        else:
            lowest_above = new_point
    logging.info(f"bisection done after {call_count} function calls")
    return lowest_above.n
