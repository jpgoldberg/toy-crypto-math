import math
from typing import Literal, assert_never

from . import types
from .utils import export

__all__: list[str] = []  # will be appended to with each definition

MAX_QBIRTHDAY_P = 1.0 - (10**-8)
"""Maximum probability that Q can handle."""


EXACT_THRESHOLD = 1000
"""With auto mode, the threshold for using exact or approximate modes."""

__all__.append("MAX_QBIRTHDAY_P")
__all__.append("EXACT_THRESHOLD")

type Mode = Literal["exact", "approximate", "auto"]
__all__.append("Mode")


def _pbirthday_exact(
    n: types.PositiveInt, classes: types.PositiveInt, coincident: int
) -> types.Prob:
    # use notation  from Diconis and Mosteller 1969
    c = classes
    k = coincident

    if k < 2:
        return types.Prob(1.0)
    if k > 2:
        return _pbirthday_approx(n, c, coincident=k)

    if n >= c:
        return types.Prob(1.0)

    v_dn = math.perm(c, n)
    v_t = c**n

    p = 1.0 - v_dn / v_t
    if not types.is_prob(p):
        assert False, f"This should not happen: p = {p}"
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

    # lifted from R src/library/stats/R/birthday.R
    LHS = n * math.exp(-n / (c * k)) / (1 - n / (c * (k + 1))) ** (1 / k)
    lxx = k * math.log(LHS) - (k - 1) * math.log(c) - math.lgamma(k + 1)
    p = -math.expm1(-math.exp(lxx))
    if not types.is_prob(p):
        assert False, f"this should not happen: p = {p}"
    return p


@export
def P(
    n: int, classes: int = 365, coincident: int = 2, mode: Mode = "auto"
) -> types.Prob:
    """probability of at least 1 collision among n individuals for c classes".

    The "exact" method still involves floating point approximations
    and may be very slow for large n.

    :raises ValueError: if any of ``n``, ``classes``,
        or ``coincident`` are less than 1.
    """
    if not types.is_positive_int(n):
        raise ValueError("n must be a positive integer")
    if not types.is_positive_int(classes):
        raise ValueError("classes must be a positive integer")
    if not types.is_positive_int(coincident):
        raise ValueError("coincident must be a positive integer")

    # Name parameters to follow # Use DM69 notation
    c = classes
    k = coincident

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
            assert_never(mode)


@export
def Q(prob: float = 0.5, classes: int = 365, coincident: int = 2) -> int:
    """Returns minimum number n to get prob for classes.

    :raises ValueError: if ``prob`` is less than 0 or greater than 1.
    :raises ValueError: if ``classes`` is less than 1.
    :raises ValueError: if ``coincident`` is less than 1.
    """
    if not types.is_prob(prob):
        raise ValueError(f"{prob} is not a valid probability")
    if not types.is_positive_int(classes):
        raise ValueError("classes must be positive")
    if not types.is_positive_int(coincident):
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
    # broken down into three terms to help me better understand
    # t_1 = c^{k-1}
    # t_2 = k!
    # t_3 = 1/log(1-p)
    # n \approx. \lceil t_1 t_2 t_3 \rceil
    #
    # All terms are computed as logarithms
    term1 = (k - 1) * math.log(c)  # log  c^{k-1}
    term2 = math.lgamma(k + 1)  # log   k!
    term3 = math.log(-math.log1p(-p))  # log  1/log(1-p)
    log_n = (term1 + term2 + term3) / k  # adding log x_i is log prod x_i
    n = math.exp(log_n)
    n = math.ceil(n)

    # n is now close to what it should be,
    # but we may need to increase it or decrease it
    # until |P(n, c, k) - p| is nearly minimized

    def pck(n: int) -> types.Prob:
        return P(n, c, coincident=k)

    if pck(n) < p:
        n += 1
        while pck(n) < p:
            n += 1
    elif pck(n - 1) >= p:
        n -= 1
        while pck(n - 1) >= p:
            n -= 1

    return n
