"""
Chinese Remainder Theorem

    In addition to being a theorem and an algorithm, we would suggest to the reader that the Chinese remainder theorem is also a state of mind.
    — Hoffstein, Pipher, and Silverman (2008)
"""

from typing import cast

from functools import lru_cache
import math

import logging
import itertools
from collections.abc import Collection, Sequence
from dataclasses import dataclass

from .. import types
from . import egcd


class Field:
    @dataclass(frozen=True, order=True)
    class _Triple:
        modulus: int  # Must be first member for ordering
        partial_product: int
        inverse: int

        def __eq__(self, other: object) -> bool:
            if not isinstance(other, Field._Triple):
                return NotImplemented
            return (
                self.modulus == other.modulus
                and self.partial_product == other.partial_product
            )

        def __hash__(self) -> int:
            return hash((self.modulus, self.partial_product))

    def __init__(self, moduli: Collection[types.PositiveInt]) -> None:
        """Creates a CRT field with respect to moduli.

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

        self._data: tuple[Field._Triple, ...] = tuple(
            [
                self._Triple(modulus=m, partial_product=p, inverse=i)
                for m, p, i in zip(self._moduli, partial_products, inverses)
            ]
        )

    def __hash__(self) -> int:
        return hash(self._data)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Field):
            return False
        return self._data == other._data

    @property
    def moduli(self) -> tuple[int, ...]:
        return self._moduli

    @property
    @lru_cache
    def inverses(self) -> tuple[int, ...]:
        return tuple([datum.inverse for datum in self._data])

    def to_int(self, remainders: Sequence[int]) -> int:
        """The smallest non-negative integer that produces these remainders

        :param remainders:
            The remainders corresponding to the *sorted* list of moduli.

        :raises ValueError:
            if the number of remainders does not match the number moduli
            for this CRT field.
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
    """An element (number) is a CRT Field."""

    def __init__(self, field: Field, remainders: Sequence[int]) -> None:
        """An element of a CRT field from remainders.

        Remainders must be ordered so that the i-th remainder corresponds
        to the i-th modulus in the field. The moduli in the field
        are sorted in ascending order.
        """
        len_r = len(remainders)
        len_m = len(field.moduli)
        if len_r != len_m:
            raise ValueError(
                f"Number of remainders ({len_r}) must match"
                f"number of moduli {len_m}."
            )
        self._field = field

        # We will reduce the given remainders
        self._remainders: tuple[int, ...] = tuple(
            [r % m for r, m in zip(remainders, self._field.moduli)]
        )

    @staticmethod
    def from_int(field: Field, n: int) -> "Element":
        if n < 1:
            raise ValueError
        remainders = [n % m for m in field.moduli]
        return Element(field, remainders)

    @property
    def field(self) -> Field:
        return self._field

    @property
    def remainders(self) -> tuple[int, ...]:
        return self._remainders

    def __int__(self) -> int:
        return self._field.to_int(self._remainders)

    def __str__(self) -> str:
        r_digits = ", ".join((str(r) for r in self._remainders))
        m_digits = ", ".join((str(m) for m in self._field.moduli))

        return f"({r_digits}) % ({m_digits}))"

    def __add__(self, other: object) -> "Element":
        # Note that we will be counting on CtrlElement initialization
        # to do any needed modular reduction.

        added: Sequence[int]
        if isinstance(other, Element):
            added = [
                cast(int, left + right)
                for (left, right) in zip(
                    self._remainders, other.remainders, strict=True
                )
            ]
        elif isinstance(other, int):
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
            added = [
                cast(int, left * right)
                for left, right in zip(self._remainders, other.remainders)
            ]
        elif isinstance(other, int):
            added = [r * other for r in self._remainders]
        else:
            return NotImplemented

        return Element(self._field, added)

    def mul(self, other: object) -> "Element":
        return self.__mul__(other)
