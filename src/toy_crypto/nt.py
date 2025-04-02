# SPDX-FileCopyrightText: 2024-present Jeffrey Goldberg <jeffrey@goldmark.org>
#
# SPDX-License-Identifier: MIT

import math
from collections import UserList
from collections.abc import Iterator, Iterable
from typing import Any, NewType, Optional, Self, TypeGuard

import primefac

try:
    from bitarray import bitarray
    from bitarray.util import count_n, ba2int
except ImportError:

    def bitarray(*args, **kwargs) -> Any:  # type: ignore
        raise NotImplementedError("bitarray is not installed")

    def count_n(*args, **kwargs) -> int:  # type: ignore
        raise NotImplementedError("bitarray is not installed")

    def ba2int(*args, **kwargs) -> int:  # type: ignore
        raise NotImplementedError("bitarray is not installed")


from . import types


Modulus = NewType("Modulus", int)
"""type Modulus is an int greater than 1"""


def is_modulus(n: Any) -> TypeGuard[Modulus]:
    if not isinstance(n, int):
        return False
    if n < 2:
        return False
    if not isprime(n):
        return False
    return True


def isprime(n: int) -> bool:
    """False if composite; True if very probably prime."""
    return primefac.isprime(n)


def isqrt(n: int) -> int:
    """returns the greatest r such that r * r =< n"""
    if n < 0:
        raise ValueError("n cannot be negative")
    return math.isqrt(n)


def modinv(a: int, m: int) -> int:
    """
    Returns b such that :math:`ab \\equiv 1 \\pmod m`.

    :raises ValueError: if a is not coprime with m
    """

    # python 3.8 allows -1 as power.
    return pow(a, -1, m)


class FactorList(UserList[tuple[int, int]]):
    """
    A FactorList is an list of (prime, exponent) tuples.

    It represents the prime factorization of a number.
    """

    def __init__(
        self,
        prime_factors: list[tuple[int, int]] = [],
        check_primes: bool = False,
    ) -> None:
        """
        prime_factors should be a list of (prime, exponent) tuples.

        Either you ensure that the primes really are prime or use
        ``check_primes = True``.
        """
        super().__init__(prime_factors)

        # Normalization will do some sanity checking as well
        self.normalize(check_primes=check_primes)

        # property-like things that are computed when first needed
        self._n: Optional[int] = None
        self._totient: Optional[int] = None
        self._radical: Optional[FactorList] = None
        self._radical_value: Optional[int] = None
        self._factors_are_prime: Optional[bool] = None

    def __repr__(self) -> str:
        s: list[str] = []
        for p, e in self.data:
            term = f"{p}" if e == 1 else f"{p}^{e}"
            s.append(term)
        return " * ".join(s)

    def __eq__(self, other: object) -> bool:
        # Implemented for
        #  - list
        #  - int
        #  - UserDict
        if isinstance(other, list):
            try:
                other_f = FactorList(other)
            except (ValueError, TypeError):
                return False
            return self.data == other_f.data

        # Fundamental theorem of arithmetic
        if isinstance(other, int):
            return self.n == other

        if not isinstance(other, UserList):
            return NotImplemented

        return self.data == other.data

    def __add__(self, other: Iterable[tuple[int, int]]) -> "FactorList":
        added = super().__add__(other)
        added = FactorList(added.data)  # init will normalize
        return added

    def normalize(self, check_primes: bool = False) -> Self:
        """
        Deduplicates and sorts in prime order, removing exponent == 0 cases.

        :raises TypeError: if prime and exponents are not ints

        :raises ValueError: if p < 2 or e < 0

        This only checks that primes are prime if ``check_primes`` is True.

        """

        # this calls for some clever list comprehensions.
        # But I am not feeling that clever at the moment

        # I will construct a dict from the data and then
        # reconstruct the data from the dict

        d = {p: 0 for (p, _) in self.data}
        for p, e in self.data:
            if not isinstance(p, int) or not isinstance(e, int):
                raise TypeError("Primes and exponents must be integers")
            if p < 2:
                raise ValueError(f"{p} should be greater than 1")
            if e == 0:
                continue
            if e < 0:
                raise ValueError(f"exponent ({e}) should not be negative")
            if check_primes:
                if not isprime(p):
                    raise ValueError(f"{p} is composite")
            d[p] += e

        self.data = [(p, d[p]) for p in sorted(d.keys())]

        return self

    @property
    def factors_are_prime(self) -> bool:
        """True iff all the alleged primes are prime."""
        if self._factors_are_prime is not None:
            return self._factors_are_prime
        self._factors_are_prime = all([isprime(p) for p, _ in self.data])
        return self._factors_are_prime

    @property
    def n(self) -> int:
        """The integer that this is a factorization of"""
        if self._n is None:
            self._n = int(math.prod([p**e for p, e in self.data]))
        return self._n

    @property
    def phi(self) -> int:
        """
        Returns Euler's Totient (phi)

        :math:`\\phi(n)` is the number of numbers
        less than n which are coprime with n.

        This assumes that the factorization (self) is a prime factorization.
        """

        if self._totient is None:
            self._totient = int(
                math.prod([p ** (e - 1) * (p - 1) for p, e in self.data])
            )

        return self._totient

    def coprimes(self) -> Iterator[int]:
        """Iterator of coprimes."""
        for a in range(1, self.n):
            if not any([a % p == 0 for p, _ in self.data]):
                yield a

    def unit(self) -> int:
        """Unit is always 1 for positive integer factorization."""
        return 1

    def is_integral(self) -> bool:
        """Always true for integer factorization."""
        return True

    def value(self) -> int:
        """Same as ``n()``."""
        return self.n

    def radical(self) -> "FactorList":
        """All exponents on factors set to 1"""
        if self._radical is None:
            self._radical = FactorList([(p, 1) for p, _ in self.data])
        return self._radical

    def radical_value(self) -> int:
        """Product of factors each used only once."""
        if self._radical_value is None:
            self._radical_value = math.prod([p for p, _ in self.data])
        return self._radical_value

    def pow(self, n: int) -> "FactorList":
        """Return (self)^n, where *n* is positive int."""
        if not types.is_positive_int(n):
            raise TypeError("n must be a positive integer")

        return FactorList([(p, n * e) for p, e in self.data])


def factor(n: int, ith: int = 0) -> FactorList:
    """
    Returns list (prime, exponent) factors of n.
    Starts trial div at ith prime.

    This wraps ``primefac.primefac()``, but creates our FactorList
    """

    primes = primefac.primefac(n)

    return FactorList([(p, 1) for p in primes])


def gcd(*integers: int) -> int:
    """Returns greatest common denominator of arguments."""
    return math.gcd(*integers)


def egcd(a: int, b: int) -> tuple[int, int, int]:
    """returns (g, x, y) such that :math:`ax + by = \\gcd(a, b) = g`."""
    x0, x1, y0, y1 = 0, 1, 1, 0
    while a != 0:
        (q, a), b = divmod(b, a), a
        y0, y1 = y1, y0 - q * y1
        x0, x1 = x1, x0 - q * x1
    return b, x0, y0


def is_square(n: int) -> bool:
    """True iff n is a perfect square."""

    return primefac.ispower(n, 2) is not None


def mod_sqrt(a: int, m: int) -> list[int]:
    """Modular square root.

    For prime m, this generally returns a list with either two members,
    :math:`[r, m - r]` such that :math:`r^2 = {(m - r)}^2 = a \\pmod m`
    if such an a is a quadratic residue the empty list if there is no such r.

    However, for compatibility with SageMath this can return a list with just
    one element in some special cases

    - returns ``[0]`` if :math:`m = 3` or :math:`a = 0`.
    - returns ``[a % m]`` if :math:`m = 2`.

    Otherwise it returns a list with the two quadratic residues if they exist
    or and empty list otherwise.

    **Warning**: The behavior is undefined if m is not prime.
    """

    match m:
        case 2:
            return [a % m]
        case 3:
            return [0]
        case _ if m < 2:
            raise ValueError("modulus must be prime")

    if a == 1:
        return [1, m - 1]

    a = a % m
    if a == 0:
        return [0]

    # check that a is a quadratic residue, return []] if not
    if pow(a, (m - 1) // 2, m) != 1:
        return []

    v = primefac.sqrtmod_prime(a, m)
    return [v, (m - v) % m]


def lcm(*integers: int) -> int:
    """Least common multiple"""

    # requires python 3.9, but I'm already requiring 3.11
    return math.lcm(*integers)
