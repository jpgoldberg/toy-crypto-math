"""
Chinese Remainder Theorem

    In addition to being a theorem and an algorithm, we would suggest to the reader that the Chinese remainder theorem is also a state of mind.
    — Hoffstein, Pipher, and Silverman (2008)
"""

from typing import cast
import math
import logging
import itertools
from collections.abc import Collection, Sequence
from dataclasses import dataclass

from ..types import PositiveInt, is_positive_int
from . import egcd
from .errors import NotInvertibleError


def solve(
    moduli: Sequence[PositiveInt], remainders: Sequence[PositiveInt]
) -> int:
    """Returns number n s.t. n = remainders[i] % moduli[i].

    :raises ValueError: if len(moduli) != len(remainders).
    :raises ValueError: if len(moduli) == 1.
    """
    len_m = len(moduli)
    if len_m != len(remainders):
        raise ValueError(
            "There must be as exactly as many remainders as moduli"
        )
    if len_m == 0:
        raise ValueError("There must be at least one modulus")

    # We could be clever an compute the big modulus and whether
    # they are mutually coprime in one loop using the Extended Euclidean
    # Algorithm, but let's not
    modulus = math.prod(moduli)
    reduced_modulus = math.lcm(*moduli)
    if modulus != reduced_modulus:
        logging.warning("Moduli are not mutually co-prime")

    result = 0
    for m, r in zip(moduli, remainders, strict=True):
        partial = modulus // m
        _, inv, _ = egcd(partial, m)
        result += r * inv * partial
        result %= modulus  # Reduce early. Reduce often.

    # A solution that is equal to the LCM is possible,
    # but can't be greater than the LCM
    if result > reduced_modulus:
        result %= reduced_modulus
    return result


class Ring:
    @dataclass(frozen=True, order=True)
    class _Triple:
        modulus: int  # Must be first member for ordering
        partial_product: int
        inverse: int

        def __eq__(self, other: object) -> bool:
            if not isinstance(other, Ring._Triple):
                return NotImplemented
            return (
                self.modulus == other.modulus
                and self.partial_product == other.partial_product
            )

        def __hash__(self) -> int:
            return hash((self.modulus, self.partial_product))

    def __init__(self, moduli: Collection[PositiveInt]) -> None:
        """Creates a CRT ring with respect to moduli.

        .. warning::

            Current implementation only supports moduli that are
            mutually co-prime with each other.

        """

        if len(moduli) == 0:
            raise ValueError("At least one modulus must be given")

        # sort and eliminate duplicates
        self._moduli: tuple[int, ...] = tuple(sorted(list(set(list(moduli)))))
        if len(self._moduli) != len(moduli):
            logging.warning(
                f"{self.__class__.__name__} initialization has duplicate moduli"
            )

        for a, b in itertools.permutations(self._moduli, 2):
            if math.gcd(a, b) != 1:
                # TODO: handle this properly. But for now just warn
                logging.warning(f"moduli {a} and {b} are not coprime")

        self._product: int = math.prod(self._moduli)

        partial_products: tuple[int, ...] = tuple(
            [self._product // m for m in self._moduli]
        )
        inverses: tuple[int, ...] = tuple(
            [egcd(p, m)[1] for p, m in zip(partial_products, self._moduli)]
        )

        self._data: tuple[Ring._Triple, ...] = tuple(
            [
                self._Triple(modulus=m, partial_product=p, inverse=inv)
                for m, p, inv in zip(self._moduli, partial_products, inverses)
            ]
        )

    def __hash__(self) -> int:
        return hash(self._data)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Ring):
            return False
        return self._data == other._data

    @property
    def moduli(self) -> tuple[int, ...]:
        return self._moduli

    @property
    def modulus(self) -> int:
        return self._product

    def element(self, value: Sequence[int] | int) -> "Element":
        """New element from either remainders or an integer."""

        if isinstance(value, Sequence):
            return Element(self, cast(Sequence[int], value))
        elif isinstance(value, int):
            return Element.from_int(self, value)
        else:
            raise TypeError("'value' must be an int or sequence of ints")

    def zero(self) -> "Element":
        """Multiplicative identity"""
        return self.element(0)

    def to_int(self, remainders: Sequence[int]) -> int:
        """The smallest non-negative integer that produces these remainders

        :param remainders:
            The remainders corresponding to the *sorted* list of moduli.

        :raises ValueError:
            if the number of remainders does not match the number moduli
            for this CRT ring.
        """
        len_r = len(remainders)
        len_m = len(self._data)
        if len_r != len_m:
            raise ValueError(
                f"Number of remainders ({len_r}) must match"
                f"number of moduli {len_m}."
            )
        x = 0
        # TODO: zip this
        for i in range(len_m):
            x += (
                remainders[i]
                * self._data[i].partial_product
                * self._data[i].inverse
            ) % self._product
        return x % self._product


class Element:
    """An element (number) is a CRT Ring."""

    def __init__(self, ring: Ring, remainders: Sequence[int]) -> None:
        """An element of a CRT ring from remainders.

        Remainders must be ordered so that the i-th remainder corresponds
        to the i-th modulus in the ring. The moduli in the ring
        are sorted in ascending order.
        """

        len_r = len(remainders)
        len_m = len(ring.moduli)
        if len_r != len_m:
            raise ValueError(
                f"Number of remainders ({len_r}) must match"
                f"number of moduli {len_m}."
            )
        self._field = ring

        # We will reduce the given remainders
        self._remainders: tuple[int, ...] = tuple(
            [r % m for r, m in zip(remainders, self._field.moduli)]
        )

        # Flagging elements to avoid recomputing things

        # Easily mark multiplicative and additive identities
        # These may get set to True in toward end of this method
        self._is_zero = False
        self._is_one = False

        # To store the multiplicative inverse, there are three cases
        # 1. The invertibility has not been computed yet.
        # 2. It has an inverse (which will be an element)
        # 3. We already know it is not invertible
        self._invertible: bool | None = None  # Case 1
        self._inverse: Element | None = None  # Case 1 or 3

        if all((r == 0 for r in self._remainders)):
            self._is_zero = True
            self._is_one = False
            self._invertible = False
            self._inverse = None

        if all((r == 1 for r in self._remainders)):
            self._is_one = True
            self._is_zero = False
            self._invertible = True
            self._mult_inverse = self

    @staticmethod
    def from_int(ring: Ring, n: PositiveInt) -> "Element":
        if not is_positive_int(n):
            raise ValueError("n must be a positive integer.")
        remainders = [n % m for m in ring.moduli]
        return Element(ring, remainders)

    @property
    def ring(self) -> Ring:
        return self._field

    @property
    def remainders(self) -> tuple[int, ...]:
        return self._remainders

    def __int__(self) -> int:
        return self._field.to_int(self._remainders)

    def __str__(self) -> str:
        r_digits = ", ".join((str(r) for r in self._remainders))
        m_digits = ", ".join((str(m) for m in self._field.moduli))

        return f"({r_digits}) % ({m_digits})"

    # *** Arithmetic ***

    # *** Arithmetic identities
    def is_zero(self) -> bool:
        """Is additive identity."""
        return self._is_zero

    def is_one(self) -> bool:
        """Multiplicative identity."""
        return self._is_one

    # *** Arithmetical operators
    def __add__(self, other: object) -> "Element":
        # Note that we will be counting on CtrlElement initialization
        # to do any needed modular reduction.

        added: Sequence[int]
        if isinstance(other, Element):
            if self._is_zero:
                return other
            if other._is_zero:
                return self
            added = [
                cast(int, left + right)
                for (left, right) in zip(
                    self._remainders, other.remainders, strict=True
                )
            ]
        elif isinstance(other, int):
            if other == 0:
                return self
            if self._is_zero:
                return self.ring.element(other)
            added = [r + other for r in self._remainders]
        else:
            return NotImplemented

        return Element(self._field, added)

    def add(self, other: object) -> "Element":
        return self.__add__(other)

    def __mul__(self, other: object) -> "Element":
        # Note that we will be counting on CtrlElement initialization
        # to do any needed modular reduction.
        if isinstance(other, Element):
            multiplied = [
                cast(int, left * right)
                for left, right in zip(self._remainders, other.remainders)
            ]
        elif isinstance(other, int):
            multiplied = [r * other for r in self._remainders]
        else:
            return NotImplemented

        return Element(self._field, multiplied)

    def mul(self, other: object) -> "Element":
        return self.__mul__(other)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, int):
            return int(self) == other % self._field._product
        elif isinstance(other, Element):
            return (self.ring == other.ring) and (
                self.remainders == other.remainders
            )
        else:
            return NotImplemented

    def mult_inverse(self) -> "Element":
        """Returns multiplicative inverse if it exists.

        :raise NotInvertibleError: if inverse does not exist.
        """

        if self._inverse:
            return self._inverse
        if not self._invertible:
            raise NotInvertibleError

        # if we reach this point, we need to attempt to compute inverse
        inverses: list[int] = list()
        for r, m in zip(self._remainders, self.ring.moduli):
            g, inv, _ = egcd(r, m)
            if g != 1:
                self._invertible = False
                raise NotInvertibleError
            inverses.append(r)
        # Yay! We have an inverse
        inverse = self.ring.element(inverses)
        self._inverse = inverse

        # And we know that self and its inverse are both invertible
        inverse._invertible = True
        inverse._inverse = self
        self._invertible = True

        return self._inverse

    def __truediv__(self, other: object) -> "Element":
        """Returns self / other if other is invertible.

        :raises ZeroDivisionError: if other is not invertible.
        """
        if isinstance(other, Element):
            try:
                return self.mul(other.mult_inverse())
            except NotInvertibleError:
                raise ZeroDivisionError

        return NotImplemented

    def div(self, other: object) -> "Element":
        """Divides by other if possible.

        :raises TypeError: if other is not a type this can handle.
        :raises ZeroDivisionError: if other is not invertible.
        """
        try:
            return self.__truediv__(other)
        except NotImplementedError:
            raise TypeError("type of 'other' cannot be a divisor")
