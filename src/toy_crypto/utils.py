from collections.abc import Generator
from typing import NewType, TypeGuard, Any
import math


def lsb_to_msb(n: int) -> Generator[int, None, None]:
    """
    Creates a generator of bits of n, starting from the least significant bit.
    """

    if not isinstance(n, int):
        raise TypeError("n must be an integer")

    if n < 0:
        raise ValueError("n cannot be negative")
    while n > 0:
        yield n & 1
        n >>= 1


def digit_count(x: float, b: int = 10) -> int:
    """returns the nunmber of  digits (base b) in the integer part of x"""

    x = abs(x)
    result = math.floor(math.log(x, base=b) + 1)
    return result


Prob = NewType("Prob", float)
PositiveInt = NewType("PositiveInt", int)


def is_prob(val: Any) -> TypeGuard[Prob]:
    """true if val is a float, s.t. 0.0 <= va <= 1.0"""
    if not isinstance(val, float):
        return False
    return val >= 0.0 and val <= 1.0


def is_positive_int(val: Any) -> TypeGuard[PositiveInt]:
    """true if val is a float, s.t. 0.0 <= va <= 1.0"""
    if not isinstance(val, int):
        return False
    return val >= 1


MAX_QBIRTHDAY_P = 1.0 - (10 ** -8)


def _pbirthday_exact(n: PositiveInt, d: PositiveInt) -> Prob:
    # use notation  from Diconis and Mosteller 1969
    c = d  # classes
    # k = 2  # coincidences

    if n >= c:
        return Prob(1.0)

    v_dn = math.perm(c, n)
    v_t = pow(c, n)

    p = 1.0 - float(v_dn / v_t)
    if not is_prob(p):
        raise Exception("this should not happen")
    return p


def _pbirthday_approx(n: PositiveInt, d: PositiveInt) -> Prob:
    # DM1969 notation
    c = d  # classes
    k = 2  # coincidences

    if n >= c * (k - 1):
        return Prob(1.0)

    # p = 1.0 - math.exp(-(n * n) / (2 * d))

    # lifted from R src/library/stats/R/birthday.R
    LHS = n * math.exp(-n/(c*k))/(1 - n/(c*(k+1))) ** (1/k)
    lxx = k*math.log(LHS) - (k-1)*math.log(c) - math.lgamma(k+1)
    p = -math.expm1(-math.exp(lxx))
    if not is_prob(p):
        raise Exception("this should not happen")
    return p


def pbirthday(n: int, d: int = 365, coincident: int = 2, mode: str = "auto") -> Prob:
    """prob of at least 1 collision among n "people" for d possible "days".

    The "exact" method still involves floating point approximations
    and may be very slow for large n.
    """

    k = coincident

    if k != 2:
        raise NotImplementedError("Not implemented for coincidence greater than 2")

    if not is_positive_int(n):
        raise ValueError("n must be a positive integer")
    if not is_positive_int(d):
        raise ValueError("d must be a possible integer")

    EXACT_THRESHOLD = 1000

    match mode:
        case "exact":
            return _pbirthday_exact(n, d)
        case "approximate":
            return _pbirthday_approx(n, d)
        case "auto" if n < EXACT_THRESHOLD:
            return _pbirthday_exact(n, d)
        case "auto":  # n >- EXACT_THRESHOLD
            return _pbirthday_approx(n, d)
        case _:
            raise ValueError('mode must be "auto", "exact", or  "approximate"')


def qbirthday(p:float = 0.5, c: int = 365, k:int = 2) -> int:
    """Returns number minimum number n to get a prob of p for c classes

    Approximation only implemented for p < 0.5
    """

    if not is_prob(p):
        raise ValueError(f'p ({p}) must be a probability')
    
    if p > MAX_QBIRTHDAY_P:
        raise NotImplementedError(f"Cannot compute for p > {MAX_QBIRTHDAY_P}")

    # Lifted from R src/library/stats/R/birthday.R
    if p == Prob(0):
        return 1
    if math.isclose(p, 1.0):
        return c * (k-1) + 1

    # Frist approximation
    n = math.exp(((k-1)*math.log(c) + math.lgamma(k+1) + math.log(-math.log1p(-p)))/k)
    n = math.ceil(n)
    if pbirthday(n, c, coincident=k) < p:
        n += 1
        while pbirthday(n, c, coincident=k) < p:
            n += 1
    elif pbirthday(n-1, c, coincident=k) >= p:
        n -= 1
        while pbirthday(n-1, c, coincident=k) >= p:
            n -= 1

    return n


   #  n = math.sqrt(2 * c * math.log(1.0/(1.0 - p)))
   # return math.ceil(n)
