"""Simple elliptic curve groups."""

import sys

if sys.version_info < (3, 11):
    raise Exception("Requires python 3.11")
from typing import Optional, Self

from toy_crypto.nt import Modulus as Modulus
from toy_crypto.nt import is_modulus, mod_sqrt
from toy_crypto.utils import lsb_to_msb


"""
This is more complicated because I unwisely attempted to make this work both
for elliptic curves defined over the reals (for the drawings) and for curves
defined over integer fields.
"""


class Curve:
    """Define a curve of the form :math:`y^2 = x^3 + ax + b \\pmod p`."""

    def __init__(self, a: int, b: int, p: int) -> None:
        self._p: Modulus = Modulus(p)
        self._a: int = a
        self._b: int = b

        if self.is_singular():
            raise ValueError(f"{self} is singular")

        if not is_modulus(self.p):
            raise ValueError("Bad modulus p")

        self._pai = Point(0, 0, self, is_zero=True)

        # This assumes (without checking) that the curve has good paramaters
        # and that a generator (base point) has been chosen correctly/
        self._order = (self.p + 1) // 2

    @property
    def a(self) -> int:
        """The 'a' of :math:`y^2 = x^3 + ax + b \\pmod p`."""
        return self._a

    @property
    def b(self) -> int:
        """The 'b' of :math:`y^2 = x^3 + ax + b \\pmod p`."""
        return self._b

    @property
    def p(self) -> Modulus:
        """The 'p' of :math:`y^2 = x^3 + ax + b \\pmod p`."""
        return self._p

    def is_singular(self) -> bool:
        return (4 * self._a**3 + 27 * self._b * self._b) % self._p == 0

    @property
    def PAI(self) -> "Point":
        """Point At Infinity"""
        return self._pai

    @property
    def order(self) -> int:
        return self._order

    def __repr__(self) -> str:
        # There is probably a nice way to do with with
        # format directives, but I'm not going to dig
        # into those docs now.
        if self._a < 0:
            ax = f"- {-self._a}x"
        else:
            ax = f"+ {self._a}"
        if self.b < 0:
            b = f"- {-self._b}x"
        else:
            b = f"+ {self.b}"

        return f"y^2 = x^3 {ax} {b} (mod {self._p})"

    def compute_y(self, x: int) -> Optional[tuple[int, int]]:
        "Returns pair of y values for x on curve. None otherwise."
        a = self._a
        b = self._b
        p = self._p
        y2: int = (pow(x, 3, p) + ((a * x) % p) + b) % p
        roots = mod_sqrt(y2, p)
        if len(roots) != 2:
            raise ValueError("x is rootless")

        return roots[0], roots[1]

    def point(self, x: int, y: int) -> "Point":
        return Point(x, y, self, is_zero=False)


class Point:
    """Point on elliptic curve over finite field."""

    # I would prefer to have all points belong to a curve
    # but I don't quite get python's classes to do that.
    # as this is all a toy, I'm not going to worry about this now

    def __init__(
        self, x: int, y: int, curve: Curve, is_zero: bool = False
    ) -> None:
        self._x: int = x
        self._y: int = y
        self._curve: Curve = curve
        self._is_zero: bool = is_zero

        if not (isinstance(self._x, int) and isinstance(self._y, int)):
            raise TypeError("Points must have integer coordinates")

        self._x %= self._curve.p
        self._y %= self._curve.p

        if not self.on_curve():
            raise ValueError("point not on curve")

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    @property
    def curve(self) -> Curve:
        return self._curve

    @property
    def is_zero(self) -> bool:
        return self._is_zero

    def on_curve(self) -> bool:
        if self._is_zero:
            return True

        x = int(self._x)
        y = int(self._y)
        a = int(self.curve.a)
        b = int(self.curve.b)

        p = self._curve.p
        # breaking this down for debugging
        lhs = pow(y, 2, p)
        rhs = (pow(x, 3, p) + a * x + b) % p

        return lhs == rhs

    # define P + Q; -P; P += Q;  P - Q; P == Q
    def __add__(self, Q: "Point") -> "Point":
        return self.add(Q)

    def __neg__(self) -> "Point":
        return self.neg()

    def __iadd__(self, Q: "Point") -> Self:
        return self.iadd(Q)

    def __sub__(self, Q: "Point") -> "Point":
        return self.__add__(Q.__neg__())

    def __eq__(self, Q: object) -> bool:
        if not isinstance(Q, Point):
            return NotImplemented
        if not self and not Q:  # both are 0
            return True
        if self._x != Q.x or self._y != Q.y:  # x's and y's don't match
            return False
        if self._curve != Q.curve:  # They are defined for different curves
            return False
        return True

    def __bool__(self) -> bool:
        """P is True iff P is not the zero point."""
        return not self._is_zero

    def __repr__(self) -> str:
        return f"({self.x}, {self.y})"

    def neg(self) -> "Point":
        """Return additive inverse.

        :returns: Additive inverse
        :rtype: Point
        """

        if self.is_zero:
            return self

        r = self.cp()
        r._y = self._curve.p - r._y
        return r

    # I don't know how shallow a copy() is in Python, so
    def cp(self) -> "Point":
        """Return a copy of self."""

        return Point(self._x, self._y, self._curve, is_zero=self._is_zero)

    def iadd(self, Q: "Point") -> Self:
        """add point to self in place.

        :raises TypeError: if Q is not a point
        :raises ValueError: if Q is not on its own curve
        :raises ValueError: if Q is on a distinct curve
        """

        # The order of checking matters, as each check is seen as
        # as a fall through of prior checks
        if not isinstance(Q, Point):
            return NotImplemented

        # We don't do curve check on Q if Q is 0
        # P + 0 = P
        if not Q:
            return self

        # if Q is not on its curve then there is something wrong with it.
        if not Q.on_curve():
            raise ValueError("Point is not on curve")

        # 0 + Q = Q
        if not self:
            self._x, self._y = Q.x, Q.y
            self._curve = Q.curve
            self._is_zero = Q.is_zero
            return self

        # if Q is on a different curve, something bad is happening
        if self.curve != Q.curve:
            raise ValueError("Points on different curves")

        # P + P
        if self == Q:
            return self.idouble()

        # P + -P = 0
        if self._x == Q.x:
            self._x, self._y = 0, 0
            self._is_zero = True
            return self

        # Generics would be better than the abuse of type
        # narrowing that I am doing here to call different
        # _addition() methods

        self._x, self._y = self._nz_addition(Q)

        return self

    def add(self, Q: "Point") -> "Point":
        """Add points.

        :param Q: Point to add
        :type Q: Point

        :returns: Sum of Q and self
        :rtype: Point
        """

        r = self.cp()
        r.iadd(Q)
        return r

    def idouble(self) -> Self:
        if self.is_zero:
            return self

        xy = self._xy_double()
        if not xy:
            self._x = 0
            self._y = 0
            self._is_zero = True
        else:
            self._x, self._y = xy

        return self

    def double(self) -> "Point":
        if self.is_zero:
            return self.cp()

        P = self.cp()
        P = P.idouble()

        return P

    def _xy_double(self) -> Optional[tuple[int, int]]:
        """(x, y) for x, y of doubled point. None if point at infinity

        :returns: new coordinates, x and y
        :rtype: Optional[tuple[int,int]]


        This does _some_ validity check of input values,
        but it might just return erroneous results the following
        conditions aren't met
        - self.curve.p is prime
        - self.curve is well defined
        - self.x, self.y are integers
        - self is on the curve
        - self is not the point at infinity
        """

        if self._is_zero:
            return None

        if self._y == 0:
            return None

        m = self._curve.p
        top = ((3 * (self._x * self._x)) % m + self._curve.a) % m
        bottom = (2 * self.y) % m
        inv_bottom = pow(bottom, m - 2, m)
        s = top * inv_bottom % m

        x = (pow(s, 2, m) - 2 * self.x) % m
        y = (s * (self.x - x) - self.y) % m

        return (x, y)

    def scaler_multiply(self, n: int) -> "Point":
        """returns n * self"""

        n = n % self.curve.order
        sum = self.curve.PAI.cp()  # additive identity
        doubled = self
        for bit in lsb_to_msb(n):
            if bit == 1:
                sum += doubled
            doubled = doubled.double()  # toil and trouble
        return sum

    def _nz_addition(self, Q: "Point") -> tuple[int, int]:
        """returns x, y over finite field Z_p"""

        if self._is_zero or Q.is_zero:
            raise ValueError("this is for non-zero points only")

        m = self.curve.p  # have the modulus handy

        # The following breaks up the point addition math into
        # gory details and steps. This helped in debugging.

        # s = (Q.y - self.y) / (Q.x - self.x)
        #   = top/bot
        #   = top * inv_bot
        #
        # And we do our mod p reductions at every opportunity
        bottom = Q.x - self.x
        # because p is prime, we can use a^{p-2} % p to compute inverse of a
        inv_bot = pow(bottom, m - 2, m)
        top = (Q.y - self.y) % m
        s = top * inv_bot % m
        s2 = (s * s) % m

        # x = (s^2 - Px) - Qx
        x = (s2 - self.x) - Q.x
        x %= m

        # y = s(Px - x) - Qy
        y = s * (self.x - x) - self.y
        y %= m

        return x, y
