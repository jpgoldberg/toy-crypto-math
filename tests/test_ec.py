import pytest
from math_utils.ec import Curve, Point, Modulus, lsb_to_msb


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
    expected = "y^2 = x^3 - 4x + 0 (mod 191)"
    name = f"{curve}"
    assert name == expected


def test_P_setup() -> None:
    P = Point(Px, Py, curve)
    exp_P = 3, 46

    assert P.x == exp_P[0]
    assert P.y == exp_P[1]


def test_compute_y() -> None:
    Qyy = curve.compute_y(Qx)
    if Qyy is None:
        pytest.fail("Qxy should exist")

    y0, y1 = Qyy

    Q0 = Point(Qx, y0, curve)
    assert Q0.on_curve()

    Q1 = Point(Qx, y1, curve)
    assert Q1.on_curve()

    assert (y0 + y1) % curve.p == 0


def test_order() -> None:
    assert curve.order == 96


def test_sums_on_curve() -> None:
    c = curve

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


def test_generation() -> None:
    c = curve

    G = Point(*(sc_generator), c)
    assert G.x == 146
    assert G.y == 131
    assert G.is_zero is False

    assert G.on_curve() is True

    for d in range(2, curve.order):
        dG = G.scaler_multiply(d)
        assert dG.on_curve()


def test_bits() -> None:
    vectors = [
        (0b1101, [1, 0, 1, 1]),
        (1, [1]),
        (0, []),
        (0o644, [0, 0, 1, 0, 0, 1, 0, 1, 1]),
    ]
    for n, expected in vectors:
        bits = [bit for bit in lsb_to_msb(n)]
        assert bits == expected


def test_double() -> None:
    G = Point(*sc_generator, curve)

    G2 = G.double()
    assert G2.x, G2.y == (8, 174)

    G4 = G2.double()
    assert G4.x, G4.y == (4, 96)



def test_scaler_multipy() -> None:
    PaI = curve.PAI
    order = curve.order
    G = Point(*(sc_generator), curve)
    oG = G.scaler_multiply(order)
    assert oG == PaI  # f'order ({order} G = {oG}'
    assert G == G.scaler_multiply(1)

    G1 = G.scaler_multiply(order + 1)
    assert G1 == G


def test_pai() -> None:
    c = curve
    PaI = c.PAI
    P = Point(Px, Py, c)
    negP = -P

    assert PaI.is_zero
    assert PaI + P == P
    assert P + PaI == P
    assert P - P == PaI
    assert negP + P == PaI


def test_validation() -> None:
    with pytest.raises(ValueError):
        Curve(2, 3, p=Modulus(31 * 73))

    with pytest.raises(ValueError):
        Curve(2, 3, p=Modulus(5))

    with pytest.raises(ValueError):
        Point(Px, Py + 1, curve)
