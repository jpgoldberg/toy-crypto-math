import pytest
from math_utils.ec import Curve, Point, Modulus


"""
Test point arithmetic on curve over Finite Fields
"""

# Curve from Serious Cryptography
sc_parameters = (-4, 0, Modulus(191))
sc_generator = (146, 131)
curve = Curve(*sc_parameters)
Px = 3
Py = 46
Qx = 146

def test_curve_repr() -> None:
    expected = 'y^2 = x^3 - 4x + 0 (mod 191)'
    name = f'{curve}'
    assert name == expected

def test_PQ_setup() -> None:
    P = Point(Px, Py, curve)
    exp_P = 3, 46

    assert P.x == exp_P[0]
    assert P.y == exp_P[1]

def test_sums_on_curve(sef) -> None:

    y = c.compute_y(Px)
    if not y:
        pytest.fail("failed to compute Py")
    else:
        Py = y[0]

    y = c.compute_y(Qx)
    if not y:
        pytest.fail("failed to compute Qy")
    else:
        Qy = y[0]

    P = Point(Px, Py, c)
    Q = Point(Qx, Qy, c)

   
    PpQ = P.add(Q)
    assert PpQ.on_curve()

    P2 = P.double()
    assert P2.on_curve()

    G = Point(*(self.sc_generator), c)
    for d in range(3, 28):
        dG = G.scaler_multiply(d)
        assert dG.on_curve()

    PaI = c.PAI
    order = (c.p + 1) // 2
    oG = G.scaler_multiply(order)
    assert oG == PaI # f'order ({order} G = {oG}'
    G1 = G.scaler_multiply(order + 1)
    assert G1 == G

def test_pai() -> None:
    c = curve
    PaI = c.PAI
    P = Point(Px, Py, c)
    negP = -P

   
    self.assertTrue(PaI.is_zero, f'PaI should be zero. Is {PaI}')

    self.assertEqual(PaI + P, P, "0 + P != P")

    self.assertEqual(P + PaI, P, "P + 0 != P")

    self.assertEqual(P - P, PaI, "P - P != 0")

    self.assertEqual(negP + P, PaI, "-P + P != 0")

def test_validation(self) -> None:

with self.subTest("Composite modulus"):
    with self.assertRaises(ValueError):
        FFCurve(2, 3, p= Modulus(31*73)) 

with self.subTest("Singular curve"):
    with self.assertRaises(ValueError):
        FFCurve(2, 3, p=Modulus(5))

c = self.curve
with self.subTest("Point not on curve"):
    with self.assertRaises(ValueError):
        Point(self.Px, self.Py + 1, c)


