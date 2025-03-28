# SPDX-FileCopyrightText: 2024-present Jeffrey Goldberg <jeffrey@goldmark.org>
#
# SPDX-License-Identifier: MIT

import math
from collections import UserList
from collections.abc import Iterator, Iterable
import gc
import threading
from typing import Any, NewType, Optional, Self, TypeGuard

import primefac

try:
    from bitarray import bitarray
    from bitarray.util import count_n
except ImportError:

    def bitarray(*args, **kwargs) -> Any:  # type: ignore
        raise NotImplementedError("bitarray is not installed")

    def count_n(*args, **kwargs) -> int:  # type: ignore
        raise NotImplementedError("bitarray is not installed")


from . import types
from . import utils


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
    return primefac.introot(n)


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
    """Returns greatest common denomenator of arguments."""
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


class Sieve:
    """Sieve of Eratosthenes.

    The good parts of this implementation are lifted from the example provided
    with the `bitarray package <https://pypi.org/project/bitarray/>`_ source.

    This depends on `bitarray package <https://pypi.org/project/bitarray/>`_.
    """

    """
    We keep the largest sieve created, which will be shared
    among all instances
    """

    _lock = threading.RLock()
    _largest_sieve = bitarray("0011")

    def _make_array(self, n: int) -> None:
        len_c = len(self._largest_sieve)
        if n <= len_c:
            return

        len_e = n - len_c

        with self._lock:
            self._largest_sieve.extend([True] * len_e)

            for i in range(2, isqrt(n) + 1):
                if self._largest_sieve[i] is False:
                    continue
                self._largest_sieve[i * i :: i] = False

    @classmethod
    def reset(cls) -> None:
        """Resets the cached array.

        There is no reason to ever use this outside of performance testing.
        """
        cls._largest_sieve = bitarray("0011")

    def __init__(self, n: int) -> None:
        """Creates sieve covering the first n integers.

        :raises ValueError: if n < 2.
        """

        if n < 2:
            raise ValueError("n must be greater than 2")

        self._make_array(n)
        self._n = n

        self._count: int = self._largest_sieve[:n].count()
        self._bitstring: Optional[str] = None

    @property
    def n(self) -> int:
        return self._n

    @property
    def array(self) -> bitarray:
        """The sieve as a bitarray."""
        return self._largest_sieve[: self._n]

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
            self._bitstring = self._largest_sieve[: self._n].to01()
        return self._bitstring

    def nth_prime(self, n: int) -> int:
        """Returns n-th prime.

        :raises ValueError: if n exceeds count.
        """

        if n > self._count:
            raise ValueError("n cannot exceed count")

        return count_n(self._largest_sieve, n)

    def primes(self, start: int = 1) -> Iterator[int]:
        """Iterator of primes starting at start-th prime.

        The 1st prime is 2. There is no zeroth prime.

        :raises ValueError: if start < 1
        """
        if start < 1:
            raise ValueError("Start must be >= 1")
        for n in range(start, self._count + 1):
            yield count_n(self._largest_sieve, n) - 1


class SetSieve:
    """Sieve of Eratosthenes using a native python set

    This consumes an enormous amount of early in initialization,
    and a SetSieve object will contain a list of prime integers,
    so even after initialization is requires more memory than the
    the integer or bitarray sieves.

    """

    """
    I may add some code to make the largest sieve created a class variable
    that can be shared by all instances.

    This means that instance methods need to be aware of the fact that the
    shared sieve may be larger than the concept within the instances.
    """

    @classmethod
    def reset(cls) -> None:
        """Reset the cached sieve.

        This is a no-op if the class doesn't
        actually cache the largest sieve created.
        """

        pass

    def __init__(self, n: int) -> None:
        """Returns sorted list primes n =< n

        A pure Python (memory hogging) Sieve of Eratosthenes.
        This consumes lots of memory, and is here only to
        illustrate the algorithm.
        """

        self._int_value: int | None = None

        self._n = n
        self._sieve: list[int] = [2, 3]
        if n < 4:
            return
        self._count: int | None = None
        # This is where the heavy memory consumption comes in.
        # Use numpy or bitarray for vast improvements in space
        # and time.
        sieve: set[int] = set(range(2, n + 1))

        # Members are rapidly deleted from the sieve at first
        # so if we periodically call the garbage collector we should
        # be able to reduce how long the holds on to the memory.
        # So let's trigger the garbage collector faster than the default
        gc.set_threshold(max(1000, gc.get_threshold()[0]))

        # We go through what remains in the sieve in numeric order,
        # eliminating multiples of what we find.
        #
        # We only need to go up to and including the square root of n,
        # remove all non-primes above that square-root =< n.
        for p in range(2, math.isqrt(n) + 1):
            if p in sieve:
                # Because we are going through sieve in numeric order
                # we know that multiples of anything less than p have
                # already been removed, so p is prime.
                # Our job is to now remove multiples of p
                # higher up in the sieve.
                for m in range(p + p, n + 1, p):
                    sieve.discard(m)

        self._sieve = sorted(sieve)

    @property
    def count(self) -> int:
        if self._count is not None:
            return self._count
        if self._n <= self._sieve[-1]:
            self._count = len(
                list((None for p in self._sieve if p <= self._n))
            )
        else:
            self._count = len(self._sieve)
        return len(self._sieve)

    def primes(self, start: int = 1) -> Iterator[int]:
        """Iterator of primes starting at start-th prime.

        The 1st prime is 2. There is no zeroth prime.

        :raises ValueError: if start < 1
        """
        if start < 1:
            raise ValueError("Start must be >= 1")

        for n in range(start, self.count + 1):
            yield self._sieve[n - 1]

    def inv_value(self) -> int:
        if self._int_value is not None:
            return self._int_value
        result = 0
        for i in range(self._n, -1, -1):
            if i in self._sieve:
                result += 1
            result <<= 1
        return result


class IntSieve:
    """A pure Python (using a large int) Sieve of Eratosthenes."""

    @classmethod
    def reset(cls) -> None:
        """Reset the cached sieve.

        This is a no-op if the class doesn't
        actually cache the largest sieve created.
        """

        pass

    def __init__(self, n: int) -> None:
        """Creates sieve of primes <= n"""

        self._length = n
        if n < 2:
            raise ValueError

        self._sieve: int = (2 ** (n + 1)) - 1
        self._sieve -= 3  # unset 0th and 1st bit.

        # We only need to go up to and including the square root of n,
        # remove all non-primes above that square-root =< n.
        for p in range(2, math.isqrt(n) + 1):
            # if utils.get_bit(self._sieve, p):
            if (self._sieve & (1 << p)) >> p:
                # Because we are going through sieve in numeric order
                # we know that multiples of anything less than p have
                # already been removed, so p is prime.
                # Our job is to now remove multiples of p
                # higher up in the sieve.
                for m in range(p + p, n + 1, p):
                    # self._sieve = utils.set_bit(self._sieve, m, False)
                    self._sieve = self._sieve & ~(1 << m)

        self._count = self._sieve.bit_count()

    def to01(self) -> str:
        """The sieve as a string of 0s and 1s.

        The output is to be read left to right. That is, it should begin with
        ``001101010001`` corresponding to primes [2, 3, 5, 7, 11]
        """

        return format(self._sieve, "b")[::-1]

    def nth_prime(self, n: int) -> int:
        """Returns n-th prime.

        :raises ValueError: if n exceeds count.
        """

        if n > self.count:
            raise ValueError("n cannot exceed count")

        result = utils.bit_index(self._sieve, n)
        assert result is not None  # because we checked n earlier
        return result

    @property
    def count(self) -> int:
        return self._count

    @property
    def n(self) -> int:
        return self._length

    def primes(self, start: int = 1) -> Iterator[int]:
        """Iterator of primes starting at start-th prime.

        The 1st prime is 2. There is no zeroth prime.

        :raises ValueError: if start < 1
        """
        if start < 1:
            raise ValueError("Start must be >= 1")
        for n in range(start, self.count + 1):
            pm = utils.bit_index(self._sieve, n)
            assert pm is not None
            yield pm
