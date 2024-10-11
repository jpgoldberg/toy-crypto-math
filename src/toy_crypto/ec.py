"""Do not use this!

Do not use this. All of this is just to provide a working context
for the scaler_multiply() method.

This is more complicated because I unwisely attempted to make this work both
for elliptic curves defined over the reals (for the drawings) and for curves
defined over integer fields.

- If you want cryptography in python use https://cryptography.io/en/latest/

- If you want to play with elliptic curves in a python-esque environment use SageMath.

Do not use the module you are looking at now for anything.
"""

import sys

if sys.version_info < (3, 11):
    raise Exception("Requires python 3.11")
from typing import Optional, Self

from toy_crypto.nt import Modulus as Modulus
from toy_crypto.nt import is_modulus, mod_sqrt
from toy_crypto.utils import lsb_to_msb


class Curve:
    """Define a curve of the form y^2 = x^3 + ax + b (mod p)."""

    def __init__(self, a: int, b: int, p: int) -> None:
        self.p: Modulus = Modulus(p)
        self.a: int = a
        self.b: int = b

        if self.is_singular():
            raise ValueError(f"{self} is singular")

        if not is_modulus(self.p):
            raise ValueError("Bad modulus p")

        self._pai = Point(0, 0, self, is_zero=True)

        # This assumes (without checking) that the curve has good paramaters
        # and that a generator (base point) has been chosen correctly/
        self._order = (self.p + 1) // 2

    def is_singular(self) -> bool:
        return (4 * self.a**3 + 27 * self.b * self.b) % self.p == 0

    @property
    def PAI(self) -> "Point":
        return self._pai

    @property
    def order(self) -> int:
        return self._order

    def __repr__(self) -> str:
        # There is probably a nice way to do with with
        # format directives, but I'm not going to dig
        # into those docs now.
        if self.a < 0:
            ax = f"- {-self.a}x"
        else:
            ax = f"+ {self.a}"

        if self.b < 0:
            b = f"- {-self.b}x"
        else:
            b = f"+ {self.b}"

        return f"y^2 = x^3 {ax} {b} (mod {self.p})"

    def compute_y(self, x: int) -> Optional[tuple[int, int]]:
        "Retruns pair of y vaules for x on curve. None otherwise."
        a = self.a
        b = self.b
        p = self.p
        y2: int = (pow(x, 3, p) + ((a * x) % p) + b) % p
        roots = mod_sqrt(y2, p)
        if len(roots) != 2:
            raise ValueError("x is rootless")

        return roots[0], roots[1]

    def point(self, x: int, y: int) -> "Point":
        return Point(x, y, self, is_zero=False)


class Point:
    """Point on elliptic curve over the reals"""

    # I would prefer to have all points belong to a curve
    # but I don't quite get python's classes to do that.
    # as this is all a toy, I'm not going to worry about this now

    def __init__(
        self, x: int, y: int, curve: Curve, is_zero: bool = False
    ) -> None:
        self.x: int = x
        self.y: int = y
        self.curve: Curve = curve
        self.is_zero: bool = is_zero

        if not (isinstance(self.x, int) and isinstance(self.y, int)):
            raise TypeError("Points must have integer coordinates")

        self.x %= self.curve.p
        self.y %= self.curve.p

        if not self.on_curve():
            raise ValueError("point not on curve")

    def on_curve(self) -> bool:
        if self.is_zero:
            return True

        x = int(self.x)
        y = int(self.y)
        a = int(self.curve.a)
        b = int(self.curve.b)

        p = self.curve.p
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
        if self.x != Q.x or self.y != Q.y:  # x's and y's don't match
            return False
        if self.curve != Q.curve:  # They are defined for different curves
            return False
        return True

    def __bool__(self) -> bool:
        """P is True iff P is not the zero point."""
        return not self.is_zero

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
        r.y = self.curve.p - r.y
        return r

    # I don't know how shallow a copy() is in Python, so
    def cp(self) -> "Point":
        """Return a copy of self."""

        return Point(self.x, self.y, self.curve, is_zero=self.is_zero)

    def iadd(self, Q: "Point") -> Self:
        """add point to self in place.

        :param Q: Point to be added
        :type Q: Point

        :returns: Point

        :raises TypeError: if Q is not a point
        :raises ValueError if P and Q are not the same subclass of Point
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
            self.x, self.y = Q.x, Q.y
            self.curve = Q.curve
            self.is_zero = Q.is_zero
            return self

        # if Q is on a different curve, something bad is happening
        if self.curve != Q.curve:
            raise ValueError("Points on different curves")

        # P + P
        if self == Q:
            return self.idouble()

        # P + -P = 0
        if self.x == Q.x:
            self.x, self.y = 0, 0
            self.is_zero = True
            return self

        # Generics would be better than the abuse of type
        # narrowing that I am doing here to call different
        # _addition() methods

        self.x, self.y = self._nz_addition(Q)

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
            self.x = 0
            self.y = 0
            self.is_zero = True
        else:
            self.x, self.y = xy

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

        if self.is_zero:
            return None

        if self.y == 0:
            return None

        m = self.curve.p
        top = ((3 * (self.x * self.x)) % m + self.curve.a) % m
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

        if self.is_zero or Q.is_zero:
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
