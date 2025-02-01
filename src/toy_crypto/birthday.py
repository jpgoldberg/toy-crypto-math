import math

from . import types


MAX_QBIRTHDAY_P = 1.0 - (10**-8)
"""Maximum probability that Q can handle."""

EXACT_THRESHOLD = 1000
"""With auto mode, the threshold for using exact or approximate modes."""


def _pbirthday_exact(
    n: types.PositiveInt, classes: types.PositiveInt, coincident: int
) -> types.Prob:
    # use notation  from Diconis and Mosteller 1969
    c = classes  # classes
    k = coincident

    if k < 2:
        return types.Prob(1.0)
    if k > 2:
        return _pbirthday_approx(n, c, coincident=k)

    if n >= c:
        return types.Prob(1.0)

    v_dn = math.perm(c, n)
    v_t = pow(c, n)

    p = 1.0 - float(v_dn / v_t)
    if not types.is_prob(p):
        raise Exception("this should not happen")
    return p


def _pbirthday_approx(
    n: types.PositiveInt, classes: types.PositiveInt, coincident: int
) -> types.Prob:
    # DM1969 notation
    c = classes
    k = coincident

    if n >= c * (k - 1):
        return types.Prob(1.0)

    if k < 2:
        return types.Prob(1.0)

    # p = 1.0 - math.exp(-(n * n) / (2 * d))

    # lifted from R src/library/stats/R/birthday.R
    LHS = n * math.exp(-n / (c * k)) / (1 - n / (c * (k + 1))) ** (1 / k)
    lxx = k * math.log(LHS) - (k - 1) * math.log(c) - math.lgamma(k + 1)
    p = -math.expm1(-math.exp(lxx))
    if not types.is_prob(p):
        raise Exception("this should not happen")
    return p


def P(
    n: int, classes: int = 365, coincident: int = 2, mode: str = "auto"
) -> types.Prob:
    """probability of at least 1 collision among n individuals for c classes".

    The "exact" method still involves floating point approximations
    and may be very slow for large n.

    :raises ValueError: if any of :data:`n`, :data:`classes`,
        or :data:`coincident` are less than 1.
    """
    c = classes
    k = coincident

    if not types.is_positive_int(n):
        raise ValueError("n must be a positive integer")
    if not types.is_positive_int(c):
        raise ValueError("classes must be a positive integer")
    if not types.is_positive_int(k):
        raise ValueError("coincident must be a positive integer")

    if k == 1:
        return types.Prob(1.0)

    if mode == "auto":
        mode = "exact" if c < EXACT_THRESHOLD else "approximate"
    match mode:
        case "exact":
            return _pbirthday_exact(n, c, coincident=k)
        case "approximate":
            return _pbirthday_approx(n, c, coincident=k)
        case _:
            raise ValueError('mode must be "auto", "exact", or  "approximate"')


def Q(prob: float = 0.5, classes: int = 365, coincident: int = 2) -> int:
    """Returns minimum number n to get a probability of p for c classes.

    :raises ValueError: if :data:`prob` is less than 0 or greater than 1.
    :raises ValueError: if :data:`classes` is less than 1.
    :raises ValueError: if :data:`coincident` is less than 1.
    """

    if not types.is_prob(prob):
        raise ValueError(f"{prob} is not a valid probability")

    if classes < 1:
        raise ValueError("classes must be positive")
    if coincident < 1:
        raise ValueError("coincident must be positive")

    # Use DM69 notation so I can better connect code to published method.
    p = prob
    c = classes
    k = coincident

    if p > MAX_QBIRTHDAY_P:
        return c * (k - 1) + 1

    # Lifted from R src/library/stats/R/birthday.R
    if p == types.Prob(0):
        return 1

    # First approximation
    # broken down so that I can better understand this.
    term1 = (k - 1) * math.log(c)  # log(c^{k-1})
    term2 = math.lgamma(k + 1)  # log k!
    term3 = math.log(-math.log1p(-p))  # ?
    log_n = (term1 + term2 + term3) / k  # adding log x_i is log prod x_i
    n = math.exp(log_n)
    n = math.ceil(n)

    if P(n, c, coincident=k) < p:
        n += 1
        while P(n, c, coincident=k) < p:
            n += 1
    elif P(n - 1, c, coincident=k) >= p:
        n -= 1
        while P(n - 1, c, coincident=k) >= p:
            n -= 1

    return n
