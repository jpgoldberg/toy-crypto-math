# SPDX-FileCopyrightText: 2024-present Jeffrey Goldberg <jeffrey@goldmark.org>
#
# SPDX-License-Identifier: MIT

"""
Number Theory (nt) module
"""

import math
from collections import UserList
from collections.abc import Generator, Iterable
from typing import Any, NewType, Optional, Self, TypeGuard

import primefac
from bitarray import bitarray
from bitarray.util import count_n

from . import types

Modulus = NewType("Modulus", int)


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
    return primefac.introot(n)


def modinv(a: int, m: int) -> int:
    """
    Returns b s.t a * b = 1 modulo m.

    Raises: ValueError if a is not coprime with m
    """

    # python 3.8 allows -1 as power.
    return pow(a, -1, m)


class FactorList(UserList[tuple[int, int]]):
    """
    A FactorList is an list of (prime, exponent) tuples.

    It representents the prime factorization of a number.

    Some of the methods here are meant to mimick what we
    see in SageMath's Factorization class, but this is
    limited to ints, and isn't always going to have the
    same behavior. If you need something as reliable and
    general and fast as SageMath's Factorization tools,
    use SageMath.
    """

    def __init__(
        self,
        prime_factors: list[tuple[int, int]] = [],
        check_primes: bool = False,
    ) -> None:
        """
        prime_factors should be a list of (prime, exponent) tuples.

        Either you ensure that the primes really are prime or use
        check_primes = True
        """
        super().__init__(prime_factors)

        # Normalization will do some sanity checking as well
        self.normalize(check_primes=check_primes)

        # properity-like things that are computed when first needed
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

        # Fundamental theorem of arithmatic
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
        Dedupicates and sorts in prime order, removing exponent == 0 cases.

        Exceptions:

            TypeError if prime and exponents are not ints

            ValueError if p < 2 or e < 0

        This only checks that primes are prime if check_primes is True.

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

        phi(n) is the number of numbers less than n which are coprime with n.

        This assumes that the factorization (self) is a prime factorization.

        """

        if self._totient is None:
            self._totient = int(
                math.prod([p ** (e - 1) * (p - 1) for p, e in self.data])
            )

        return self._totient

    def coprimes(self) -> Generator[int, None, None]:
        for a in range(1, self.n):
            if not any([a % p == 0 for p, _ in self.data]):
                yield a

    def unit(self) -> int:
        """We only handle positive integers, so"""
        return 1

    def is_integral(self) -> bool:
        return True

    def value(self) -> int:
        return self.n

    def radical(self) -> "FactorList":
        """All exponenents on factors set to 1"""
        if self._radical is None:
            self._radical = FactorList([(p, 1) for p, _ in self.data])
        return self._radical

    def radical_value(self) -> int:
        if self._radical_value is None:
            self._radical_value = math.prod([p for p, _ in self.data])
        return self._radical_value

    def pow(self, n: int) -> "FactorList":
        """Return self ** n, where n is positive int"""
        if not types.is_positive_int(n):
            raise TypeError("n must be a positive integer")

        return FactorList([(p, n * e) for p, e in self.data])


def factor(n: int, ith: int = 0) -> FactorList:
    """
    Returns list (prime, exponent) factors of n.
    Starts trial div at ith prime.

    This wraps primefac.primefac(), but creates our FactorList
    """

    primes = primefac.primefac(n)

    return FactorList([(p, 1) for p in primes])


def gcd(*integers: int) -> int:
    """Returns greatest common denomenator of arguments."""
    return math.gcd(*integers)


def egcd(a: int, b: int) -> tuple[int, int, int]:
    """returns (g, x, y) such that a*x + b*y = gcd(a, b) = g."""
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
    """For odd prime m return (r, m-r) s.t. r^2 = a (mod m) if r exists.

    m must be prime. If m is not prime, you might get a nice error,
    but sometimes you will get garbage results.
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


class Sieve:
    """Sieve of Eratosthenes"""

    ## We keep the largest sieve created, which will be shared
    ## among all instances
    _cached_array = bitarray("0011")

    def _make_array(self, n: int) -> None:
        len_c = len(self._cached_array)
        if n <= len_c:
            return

        len_e = n - len_c
        # Not thread safe. Need to make this atomic
        self._cached_array.extend([True] * len_e)

        for i in range(2, isqrt(n) + 1):
            if self._cached_array[i] is False:
                continue
            self._cached_array[i * i :: i] = False

    @classmethod
    def clear(cls) -> None:
        """Resets the cached array.

        There is no reason to every use this outside of performance testing.
        """
        cls._cached_array = bitarray("0011")

    def __init__(self, n: int) -> None:
        if not isinstance(n, int):
            raise TypeError
        if n < 2:
            raise ValueError("n must be greater than 2")

        self._make_array(n)
        self._n = n

        self._count: int = self._cached_array[:n].count()
        self._bitstring: Optional[str] = None

    @property
    def n(self) -> int:
        return self._n

    @property
    def array(self) -> bitarray:
        """The sieve as a bitarray."""
        return self._cached_array[: self._n]

    @property
    def count(self) -> int:
        """The number of primes in the sieve."""
        return self._count

    def to01(self) -> str:
        """The sieve as a string of 0s and 1s.

        The output is to be read left to right. That is, it should begin with
        ``001101010001`` corresponding to primes [2, 3, 5, 7, 11]
        """

        if self._bitstring is None:
            self._bitstring = self._cached_array[: self._n].to01()
        return self._bitstring

    def nth_prime(self, n: int) -> int:
        """Returns n-th prime.

        Raises ValueError if n exceeds count.
        """

        if n > self._count:
            raise ValueError("n cannot exceed count")

        return count_n(self._cached_array, n)
