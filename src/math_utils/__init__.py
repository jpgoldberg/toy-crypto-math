# SPDX-FileCopyrightText: 2024-present Jeffrey Goldberg <jeff@agilebits.com>
#
# SPDX-License-Identifier: MIT

from math import floor, ceil, sqrt
from functools import reduce
from collections.abc import Iterable
from collections import UserList
from typing import Self
import random  # random is good enough for Miller-Rabin.


# E731 tells me to def prod instead of bind it to a lambda.
# https://docs.astral.sh/ruff/rules/lambda-assignment/
def prod[T](iterable: Iterable[T]) -> T:
    """Returns the product of the elements of it"""
    return reduce(lambda a, b: a * b, iterable)  # type: ignore


class FactorList(UserList):

    def __init__(self, prime_factors: list[tuple[int,int]] = []):
        super().__init__(prime_factors)

        # Normalization will do some sanity checking as well
        self.normalize()

        # properity-like things that are computed when first needed
        self._n: int | None = None
        self._totient: int | None = None
        self._radical: 'FactorList | None' = None
        self._radical_value: int | None = None

    def __repr__(self) -> str:
        s: list[str] = []
        for p, e in self.data:
            term = f'{p}' if e == 1 else f'{p}^{e}'
            s.append(term)
        return ' * '.join(s)

    def normalize(self) -> Self:
        """
        Dedupicates primes and sorts in prime order.

        Exceptions:

            TypeError if prime and exponents are not ints

            ValueError if p < 2 or e < 1

        This does not check that the primes are actually prime.

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
            if e < 1:
                raise ValueError(f'{e} should be greater than 0')
            d[p] += e

        self.data = [(p, d[p]) for p in sorted(d.keys())]

        return self

    @property
    def n(self) -> int:
        if self._n is None:
            self._n = prod([p ** e for p, e in self.data])
        return self._n

    @property
    def phi(self) -> int:
        """
        Returns Euler's Totient (phi)

        phi(n) is the number of numbers less than n which are coprime with n.

        This assumes that the factorization (self) is a prime factorization.

        """

        if self._totient is None:
            self._totient = prod([p ** (e - 1) * (p - 1)
                                  for p, e in self.data])

        return self._totient

    # some aliases and such to implement a few more
    # of the SageMath Factorization methods

    def unit(self) -> int:
        """We only handle positive integers, so"""
        return 1

    def is_integral(self) -> bool:
        return True

    def value(self):
        return self.n

    def radical(self) -> 'FactorList':
        '''All exponenents on factors set to 1'''
        if self._radical is None:
            self._radical = FactorList([(p, 1) for p, _ in self.data])
        return self._radical

    def radical_value(self) -> int:
        if self._radical_value is None:
            self._radical_value = prod([p for p, _ in self.data])
        return self._radical_value


def factor(n: int, ith: int = 0) -> FactorList:
    """
    Returns list (prime, exponent) factors of n.
    Starts trial div at ith prime.
    """

    if not isinstance(n, int):
        raise TypeError('input must be an int')
    if n < 1:
        raise ValueError('input must be positive')
    if n == 1:
        return FactorList([])

    low_primes: list[int] = [
        2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61,
        67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137,
        139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211,
        223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283,
        293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379,
        383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461,
        463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563,
        569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643,
        647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739,
        743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829,
        839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937,
        941, 947, 953, 967, 971, 977, 983, 991, 997, 1009, 1013, 1019, 1021,
        1031, 1033, 1039, 1049, 1051, 1061, 1063, 1069, 1087, 1091, 1093, 1097,
        1103, 1109, 1117, 1123, 1129, 1151, 1153, 1163, 1171, 1181, 1187, 1193,
        1201, 1213, 1217, 1223, 1229, 1231, 1237, 1249, 1259, 1277, 1279, 1283,
        1289, 1291, 1297, 1301, 1303, 1307, 1319, 1321, 1327, 1361, 1367, 1373,
        1381, 1399, 1409, 1423, 1427, 1429, 1433, 1439, 1447, 1451, 1453, 1459,
        1471, 1481, 1483, 1487, 1489, 1493, 1499, 1511, 1523, 1531, 1543, 1549,
        1553, 1559, 1567, 1571, 1579, 1583, 1597, 1601, 1607, 1609, 1613, 1619,
        1621, 1627, 1637, 1657, 1663, 1667, 1669, 1693, 1697, 1699, 1709, 1721,
        1723, 1733, 1741, 1747, 1753, 1759, 1777, 1783, 1787, 1789, 1801, 1811,
        1823, 1831, 1847, 1861, 1867, 1871, 1873, 1877, 1879, 1889, 1901, 1907,
        1913, 1931, 1933, 1949, 1951, 1973, 1979, 1987, 1993, 1997, 1999, 2003,
        2011, 2017, 2027, 2029, 2039,
    ]

    factors = FactorList()
    if n in low_primes:
        return FactorList([(n, 1)])

    top = ceil(sqrt(n))

    if ith < len(low_primes):
        for ith, p in enumerate(low_primes[ith:]):
            if p > top:
                break
            reduced, remainder = divmod(n, p)
            if remainder == 0:
                exponent = 0
                prev_reduced = reduced
                while remainder == 0:
                    exponent += 1
                    prev_reduced = reduced
                    reduced, remainder = divmod(reduced, p)
                factors.append((p, exponent))
                return factors + factor(prev_reduced, ith)

    # n is not divisible by any of our low primes
    if n <= low_primes[-1] ** 2:  # n is prime
        return FactorList([(n, 1)])

    # Now we use Fermat's method (in the form of OLF
    # Note that OLF finds a (possibly composite factor),
    # So we will need to recurse and combine results.

    # OLE is a really, really, really slow way to test primality.
    # So we will do Miller-Rabin first

    if miller_rabin(n):
        return FactorList([(n, 1)])

    f = OLF(n)
    if f == 1:  # n is prime
        return FactorList([(n, 1)])

    return (factor(f) + factor(n//f)).normalize()


def gcd(a: int, b: int) -> int:
    """Returns greatest common denomenator of a and b."""
    while a != 0:
        a, b = b % a, a
    return b


def egcd(a: int, b: int) -> tuple[int, int, int]:
    """returns (g, x, y) such that a*x + b*y = gcd(a, b) = g."""
    x0, x1, y0, y1 = 0, 1, 1, 0
    while a != 0:
        (q, a), b = divmod(b, a), a
        y0, y1 = y1, y0 - q * y1
        x0, x1 = x1, x0 - q * x1
    return b, x0, y0


def modinv(a: int, m: int) -> int:
    """returns x such that a * x mod m = 1,"""
    g, x, _ = egcd(a, m)
    if g != 1:
        raise ValueError(f'{a} and {m} are not co-prime')
    return x


def is_square(n: int) -> bool:
    """
    True iff n is a perfect square.

    This may become unreliable for very large n"""
    r = sqrt(float(n))
    rr = int(round(r))
    return rr * rr == n


# From https://programmingpraxis.com/2014/01/28/harts-one-line-factoring-algorithm/
def OLF(n) -> int:
    """Returns 1 if n is prime, else a factor (possibly composite) of n"""
    for ni in range(n, n*n, n):
        cs = ceil(sqrt(ni))
        pcs = pow(cs, 2, n)
        if is_square(pcs):
            return gcd(n, floor(cs - sqrt(pcs)))

    # This will never be reached, but linters don't know that
    return 1


# lifted from https://gist.github.com/Ayrx/5884790
# k of 40 seems really high to me, but I see that the recommendation is from
# Thomas Pornin, so I am going to use that.
def miller_rabin(n: int, k: int = 40) -> bool:
    """Returns True if n is prime or if you had really bad luck."""

    # Implementation uses the Miller-Rabin Primality Test
    # The optimal number of rounds for this test is 40
    # See https://stackoverflow.com/a/6330138/1304076
    # for justification

    # If number is even, it's a composite number

    if n == 2:
        return True

    if n % 2 == 0:
        return False

    r, s = 0, n - 1
    while s % 2 == 0:
        r += 1
        s //= 2
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, s, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True
