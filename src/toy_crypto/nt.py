# SPDX-FileCopyrightText: 2024-present Jeffrey Goldberg <jeffrey@goldmark.org>
#
# SPDX-License-Identifier: MIT

import math
import secrets
from collections import UserList
from collections.abc import Iterator, Iterable
from typing import Any, Generator, NewType, Optional, Self, TypeGuard

import primefac

from . import rand

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


# lifted from https://gist.github.com/Ayrx/5884790
def probably_prime(n: int, k: int = 4) -> bool:
    """Returns True if n is prime or if you had really bad luck.

    Runs the Miller-Rabin primality test with k trials.

    :param n: The number we are checking.
    :param k: The number of random bases to test against.
    :raises ValueError: if :math:`k < 1`.

    If you need a real primality check, use sympy.isprime() instead.
    """

    if n < 2:
        return False

    if k < 1:
        raise ValueError("k must be greater than 0")

    # Let's deal with some very low primes
    # I don't want to do Fermat for tiny numbers
    # so we do trial division for primes <= 13
    small_primes = (2, 3, 5, 7, 11, 13)
    largest_small = small_primes[-1]
    if n in small_primes:
        return True
    if n < largest_small:
        return False
    for p in small_primes:
        if n % p == 0:
            return False
    if n <= largest_small**2:
        return True

    # Set up generator for k trial bases
    bases: Generator[int, None, None]
    if k >= n - 2:
        # This case should only come up for testing very small numbers
        # or using weirdly large k, but let's handle it nicely anyway.
        bases = (b for b in range(2, n - 1))
    else:
        bases = (rand.randrange(2, n) for _ in range(k))

    # This s reduction is what distinguishes M-R from FLT
    r, s = 0, n - 1
    while s % 2 == 0:
        r += 1
        s //= 2

    # Now we use FLT for the reduced s, but still mod n
    for a in bases:
        x = pow(a, s, n)
        if x == 1 or x == n - 1:
            # This a is good. Call the next witness!
            continue

        # square x for each time we reduced s for a passing x
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                # Our _a_ really was good, once we tested squares of x
                break
        else:
            # We've exited the loop without finding _a_ to be good
            return False

    # We've run all k trials, without any a telling us n is composite
    return True


def fermat_test(n: int, k: int = 8) -> bool:
    """Returns true if n is prime, a Carmichael number, or through bad luck.

    Fermat's primality tests

    :param n: The number we are checking
    :param k: The number of bases to test against.

    :raises ValueError: if :math:`k < 1`

    .. warning::

        Fermat's primality is much more prone to falsely
        claiming that a number is prime than other, equally
        efficient, tests.

        Its only advantage is that it is easier to understand.
    """

    if n < 2:
        return False

    # I don't want to do Fermat for tiny numbers
    # so we do trial division for primes <= 13
    small_primes = (2, 3, 5, 7, 11, 13)
    largest_small = small_primes[-1]
    if n in small_primes:
        return True
    if n < largest_small:
        return False
    for p in small_primes:
        if n % p == 0:
            return False
    if n <= largest_small**2:
        return True

    # Now we are ready for Fermat's test
    if k < 1:
        raise ValueError("k must be greater than 0")

    # Set up generator for k trial bases
    bases: Generator[int, None, None]
    if k >= n - 2:
        # This case should only come up for testing very small numbers
        # or using weirdly large k, but let's handle it nicely anyway.
        bases = (b for b in range(2, n - 1))
    else:
        bases = (rand.randrange(2, n) for _ in range(k))

    # Fermat's Little Theorem says
    # if p is prime then a^(p-1) = 1 (mod p) for all a
    for a in bases:
        if pow(a, n - 1, n) != 1:
            return False

    return True


def get_prime(
    bit_size: int, k: int = 4, leading_1_bits: int = 1, e: int = 1
) -> int:
    """Return a randomly chosen prime of :data:`bit_size` bits.

    :param bit_size: Size in bits of the prime to be generated
    :param k: Number of witnesses to primality we require.
    :param leading_1_bits: How many most significant bits should be set.
    :param e:
        Number which gcd(prime -1, e) must be 1. Default of 1 places no
        restriction on the prime.

    The produces primes for which the leading two bits are 1.
    So it is not a uniform distribution of primes in the range
    """

    if leading_1_bits >= bit_size:
        raise ValueError("leading_1_bits must be less than bit_size")

    # might lower this in future and just choose from list of primes
    if bit_size < 8:
        raise ValueError("bit_size must be at least 8")

    if leading_1_bits < 0:
        raise ValueError("leading_1_bits can't be negative")

    if e < 1 or e.bit_length() >= bit_size:
        raise ValueError("e is out of range")

    if e % 2 == 0:
        raise ValueError("e must be odd")

    # Things that will make it harder (or impossible) to find a prime
    # - Small bit_size
    # - Large leading_1_bits (relative to bit_size)
    # - e with small factor(s) (note that default of 1 has no factors)
    #
    # So we will put a limit on searching on the number of primality tests
    # we will run.
    prime_test_limit = 10 * (bit_size - leading_1_bits)
    prime_test_count = 0

    n: int
    while True:  # Until we find a prime
        # We will construct a random number of the right size and then test it.

        # We want our constructed number to have leading_one_bits of leading 1s
        n = secrets.randbits(bit_size - leading_1_bits)

        prefix = (2**leading_1_bits) - 1
        n += prefix << (bit_size - leading_1_bits)

        # Well, this is a special case, innit?
        if n == 2:
            return n

        # Make it odd
        if n % 2 == 0:
            n += 1

        if gcd(n - 1, e) != 1:
            continue

        if probably_prime(n, k):
            break
        prime_test_count += 1
        if prime_test_count > prime_test_limit:
            raise Exception("failed to find prime meeting all conditions")
    return n
