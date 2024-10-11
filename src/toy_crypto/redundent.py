# SPDX-FileCopyrightText: 2024-present Jeffrey Goldberg <jeffrey@goldmark.org>
#
# SPDX-License-Identifier: MIT

"""
Redundant definitions

Things here have been replace by what is in the nt module,
which wraps other, better implementations (mostly from primefac and math)
"""

import random  # random is good enough for Miller-Rabin.

from . import nt, types

# Generics require Python 3.12+, and it is hard to please type checkers here,
# So I am getting rid of this.

# E731 tells me to def prod instead of bind it to a lambda.
# https://docs.astral.sh/ruff/rules/lambda-assignment/
# def prod[T](iterable: Iterable[T]) -> T:  # type: ignore
#    """Returns the product of the elements of it"""
#    return reduce(lambda a, b: a * b, iterable)


# primes under 2^21
LOW_PRIMES: list[int] = [
    2,
    3,
    5,
    7,
    11,
    13,
    17,
    19,
    23,
    29,
    31,
    37,
    41,
    43,
    47,
    53,
    59,
    61,
    67,
    71,
    73,
    79,
    83,
    89,
    97,
    101,
    103,
    107,
    109,
    113,
    127,
    131,
    137,
    139,
    149,
    151,
    157,
    163,
    167,
    173,
    179,
    181,
    191,
    193,
    197,
    199,
    211,
    223,
    227,
    229,
    233,
    239,
    241,
    251,
    257,
    263,
    269,
    271,
    277,
    281,
    283,
    293,
    307,
    311,
    313,
    317,
    331,
    337,
    347,
    349,
    353,
    359,
    367,
    373,
    379,
    383,
    389,
    397,
    401,
    409,
    419,
    421,
    431,
    433,
    439,
    443,
    449,
    457,
    461,
    463,
    467,
    479,
    487,
    491,
    499,
    503,
    509,
    521,
    523,
    541,
    547,
    557,
    563,
    569,
    571,
    577,
    587,
    593,
    599,
    601,
    607,
    613,
    617,
    619,
    631,
    641,
    643,
    647,
    653,
    659,
    661,
    673,
    677,
    683,
    691,
    701,
    709,
    719,
    727,
    733,
    739,
    743,
    751,
    757,
    761,
    769,
    773,
    787,
    797,
    809,
    811,
    821,
    823,
    827,
    829,
    839,
    853,
    857,
    859,
    863,
    877,
    881,
    883,
    887,
    907,
    911,
    919,
    929,
    937,
    941,
    947,
    953,
    967,
    971,
    977,
    983,
    991,
    997,
    1009,
    1013,
    1019,
    1021,
    1031,
    1033,
    1039,
    1049,
    1051,
    1061,
    1063,
    1069,
    1087,
    1091,
    1093,
    1097,
    1103,
    1109,
    1117,
    1123,
    1129,
    1151,
    1153,
    1163,
    1171,
    1181,
    1187,
    1193,
    1201,
    1213,
    1217,
    1223,
    1229,
    1231,
    1237,
    1249,
    1259,
    1277,
    1279,
    1283,
    1289,
    1291,
    1297,
    1301,
    1303,
    1307,
    1319,
    1321,
    1327,
    1361,
    1367,
    1373,
    1381,
    1399,
    1409,
    1423,
    1427,
    1429,
    1433,
    1439,
    1447,
    1451,
    1453,
    1459,
    1471,
    1481,
    1483,
    1487,
    1489,
    1493,
    1499,
    1511,
    1523,
    1531,
    1543,
    1549,
    1553,
    1559,
    1567,
    1571,
    1579,
    1583,
    1597,
    1601,
    1607,
    1609,
    1613,
    1619,
    1621,
    1627,
    1637,
    1657,
    1663,
    1667,
    1669,
    1693,
    1697,
    1699,
    1709,
    1721,
    1723,
    1733,
    1741,
    1747,
    1753,
    1759,
    1777,
    1783,
    1787,
    1789,
    1801,
    1811,
    1823,
    1831,
    1847,
    1861,
    1867,
    1871,
    1873,
    1877,
    1879,
    1889,
    1901,
    1907,
    1913,
    1931,
    1933,
    1949,
    1951,
    1973,
    1979,
    1987,
    1993,
    1997,
    1999,
    2003,
    2011,
    2017,
    2027,
    2029,
    2039,
]

MAX_LOW_PRIME_SQUARE = LOW_PRIMES[-1] * LOW_PRIMES[-1]


def factor(n: int, ith: int = 0) -> nt.FactorList:
    """
    Returns list (prime, exponent) factors of n.
    Starts trial div at ith prime.

    This uses trial division by low primes for things upto the square
    of the largeest low primes and uses Fermet's method for everything else.
    Fermat's method is really bad when the
    factors are far away from each other, so my low primes list
    is longer than would make sense for other factoring strategies
    """

    if not types.is_positive_int(n):
        raise TypeError("input must be a positive int")

    if n == 1:
        return nt.FactorList([])

    factors = nt.FactorList()
    if n in LOW_PRIMES:
        return nt.FactorList([(n, 1)])

    root_n = isqrt(n)
    if root_n * root_n == n:
        return factor(root_n).pow(2)
    top = root_n

    if ith < len(LOW_PRIMES):
        for ith, p in enumerate(LOW_PRIMES[ith:]):
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
    if n <= LOW_PRIMES[-1] ** 2:  # n is prime
        return nt.FactorList([(n, 1)])

    # Now we use Fermat's method (in the form of OLF
    # Note that OLF finds a (possibly composite factor),
    # So we will need to recurse and combine results.

    # OLE is a really, really, really slow way to test primality.
    # So we will do Miller-Rabin first
    if probably_prime(n):
        return nt.FactorList([(n, 1)])

    f = OLF(n)
    if f == 1:  # n is prime
        # This shouldn't happen, as we've already checked for primality
        # But I am leaving it in in case I somehow remove the
        # earlier primality check.
        return nt.FactorList([(n, 1)])

    return factor(f) + factor(n // f)


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
        raise ValueError(f"{a} and {m} are not co-prime")
    return x % m


# from https://en.wikipedia.org/wiki/Integer_square_root
def isqrt(s: int) -> int:
    """returns the greatest n such that n * n =< s"""
    if s < 0:
        raise ValueError("s cannot be negative")
    if not isinstance(s, int):
        raise TypeError("s must be an int")

    if s < 2:
        return s

    x0: int = pow(2, (s.bit_length() // 2) + 1)
    x1: int = (x0 + s // x0) // 2

    while x1 < x0:
        x0 = x1
        x1 = (x0 + s // x0) // 2

    return x0


def is_square(n: int) -> bool:
    """True iff n is a perfect square."""

    # We can eliminate some quickly as
    #  - even squares must be 0 mod 4
    #  - odd squares must be 1 mod 8
    if n % 2 == 0:
        if n % 4 != 0:
            return False
    elif n % 8 != 1:
        return False

    r = isqrt(n)
    return r * r == n


# From https://programmingpraxis.com/2014/01/28/harts-one-line-factoring-algorithm/
def OLF(n: int) -> int:
    """Returns 1 if n is prime, else a factor (possibly composite) of n"""
    for ni in range(n, n * n, n):
        cs = isqrt(ni)
        # isqrt(x) gives us floor(sqrt(x)), but we need ceil(sqrt(n))
        if cs * cs != ni:
            cs += 1
        pcs = pow(cs, 2, n)
        if is_square(pcs):
            return gcd(n, cs - isqrt(pcs))

    # This will never be reached, but linters don't know that
    return 1


# lifted from https://gist.github.com/Ayrx/5884790
# k of 40 seems really high to me, but I see that the recommendation is from
# Thomas Pornin, so I am going to use that.
def probably_prime(n: int, k: int = 40) -> bool:
    """Returns True if n is prime or if you had really bad luck.

    Runs the Miller-Rabin primality test with k trials.
    Default value of k=40 is appropriate for use in key generation,
    but may be way high in other contexts.

    If you need a real primality check, use sympy.isprime() instead.
    """

    if n == 2:
        return True

    if n in LOW_PRIMES:
        return True
    if n <= MAX_LOW_PRIME_SQUARE:
        for p in LOW_PRIMES:
            if n % p == 0:
                return False
        return True

    # This s reduction is what distinguishes M-R from FLT
    r, s = 0, n - 1
    while s % 2 == 0:
        r += 1
        s //= 2

    # Now we use FLT for the reduced s, but still mod n
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, s, n)
        if x == 1 or x == n - 1:
            # This a is good. Call the next witness!
            continue

        # square x for each time we reduced s for a passing x
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                # Our a really was good, once we tested squares of x
                break
        else:
            # We've exited the loop without finding a to be good
            return False

    # We've run all k trials, without any a telling us n is composite
    return True


def mod_sqrt(a: int, m: int) -> list[int]:
    """For odd prime m return (r, m-r) s.t. r^2 = a (mod m) if r exists.

    m must be an odd prime. If p is not prime, you might get a nice error,
    but sometimes you will get garbage results.
    """

    # I would have thought that there was a library for this.
    # Can't find it outside of sage, which is a bit big to import.

    # Algorithm taken from https://www.rieselprime.de/ziki/Modular_square_root

    if m < 3:
        raise ValueError("modulus must be an odd prime")

    if a == 1:
        return [1, m - 1]

    if m == 3:
        return []

    a = a % m
    if a == 0:
        return [0]

    # Use a small k, as we aren't claiming a definitive test
    if not probably_prime(m, k=5):
        raise ValueError("m is not prime")

    # check that a is a quadratic residue, return None if not
    if pow(a, (m - 1) // 2, m) != 1:
        return []

    if m % 4 == 3:  # if r exists then r = a^{(m+1)/2}
        r = pow(a, (m + 1) // 4, m)
        return [r, (m - r) % m]

    # Now we move to the tricky cases
    if m % 8 == 5:
        v = pow(2 * a, (m - 5) // 8, m)
        i = (2 * a * v * v) % m
        r = (a * v * (i - 1)) % m
        return [r, (m - r) % m]

    if m % 8 != 1:
        raise ValueError("modulus must be prime")

    # Now we are at the m % 8 == 1 case for which the algorithm is messy
    # Instructions quoted from
    #     https://www.rieselprime.de/ziki/Modular_square_root

    # Step 1: "Set e and odd q s.t. m = (2^e)q + 1"
    # Well, thanks. Let's figure out how to do that.

    # m is odd so we know that (2^1)q + 1 = m has
    # an integer q. So we start there
    e = 1
    q = (m - 1) // 2
    # while q is even if cut it in half and increment e
    while q % 2 == 0:
        e += 1
        q //= 2  # could do q >>= 1, but compiler will pick that if faster

    # just a check that we got an e and q
    if m != (2**e) * q + 1:
        raise Exception(f"Shouldn't happen: 2^{e} * {q} + 1 != {m}")
    if q % 2 == 0:
        raise Exception(f"Shouldn't happen: q ({q}) isn't odd.")

    # Step 2.
    # Find an x such that x is a quadratic non-residue of m.
    # We don't need good randomness, and half of possible x
    # are quadratic non-residues
    x: int = random.randint(2, m - 1)
    z: int = pow(x, q, m)
    while pow(z, 2 ** (e - 1), m) == 1:
        x = random.randint(2, m - 1)
        z = pow(x, q, m)

    # step 3:
    # x should now be a QNR in Zm
    y = z
    r = e
    x = pow(a, (q - 1) // 2, m)
    v = (a * x) % m
    w = (v * x) % m

    # step 4:
    # I do not understand why this all works.
    while w != 1:
        # step 5: "Find the smallest value of k such that w^(2^k) % m == 1"
        k = 1
        w2 = w * w
        while w2 % m != 1:
            w2 *= w2
            k += 1
        # step 6:
        d = pow(y, 2 ** (r - k - 1), m)
        y = (d * d) % m
        r = k
        v = (d * v) % m
        w = (w * y) % m

    return [v, (m - v) % m]


def lcm(a: int, b: int) -> int:
    """Least common multiple"""
    return abs(a * b) // gcd(a, b)
