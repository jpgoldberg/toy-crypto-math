import pytest
from math_utils.ec import Curve, Point, Modulus, lsb_to_msb
from math_utils import is_square


class TestSeriousCurve:
    """
    Tests involving example curve from Serious Cryptography
    """

    sc_parameters = (-4, 0, Modulus(191))
    sc_generator = (146, 131)
    curve = Curve(*sc_parameters)
    G = Point(*sc_generator, curve)
    Px = 3
    Py = 46
    Qx = 146

    # Computed using SageMath
    sage_vectors: dict[int, tuple[int, int]] = {
        1: (146, 131), 2: (8, 174), 3: (137, 161), 4: (4, 96), 5: (61, 163), 6: (34, 83), 7: (171, 22), 8: (18, 52), 9: (174, 180), 10: (77, 133), 11: (186, 75), 12: (136, 46), 13: (29, 4), 14: (48, 57), 15: (155, 61), 16: (158, 26), 17: (71, 120), 18: (102, 69), 19: (179, 109), 20: (15, 100), 21: (122, 124), 22: (3, 46), 23: (87, 55), 24: (79, 33), 25: (74, 114), 26: (10, 177), 27: (53, 110), 28: (32, 172), 29: (56, 98), 30: (25, 98), 31: (99, 177), 32: (100, 80), 33: (42, 167), 34: (52, 145), 35: (165, 10), 36: (156, 184), 37: (110, 98), 38: (160, 79), 39: (82, 177), 40: (98, 121), 41: (19, 174), 42: (50, 29), 43: (164, 17), 44: (6, 1), 45: (111, 188), 46: (67, 166), 47: (140, 38), 48: (2, 0), 49: (140, 153), 50: (67, 25), 51: (111, 3), 52: (6, 190), 53: (164, 174), 54: (50, 162), 55: (19, 17), 56: (98, 70), 57: (82, 14), 58: (160, 112), 59: (110, 93), 60: (156, 7), 61: (165, 181), 62: (52, 46), 63: (42, 24), 64: (100, 111), 65: (99, 14), 66: (25, 93), 67: (56, 93), 68: (32, 19), 69: (53, 81), 70: (10, 14), 71: (74, 77), 72: (79, 158), 73: (87, 136), 74: (3, 145), 75: (122, 67), 76: (15, 91), 77: (179, 82), 78: (102, 122), 79: (71, 71), 80: (158, 165), 81: (155, 130), 82: (48, 134), 83: (29, 187), 84: (136, 145), 85: (186, 116), 86: (77, 58), 87: (174, 11), 88: (18, 139), 89: (171, 169), 90: (34, 108), 91: (61, 28), 92: (4, 95), 93: (137, 30), 94: (8, 17), 95: (146, 60)
    }

    def test_curve_repr(self) -> None:
        expected = "y^2 = x^3 - 4x + 0 (mod 191)"
        name = f"{self.curve}"
        assert name == expected

    def test_P_setup(self) -> None:
        P = Point(self.Px, self.Py, self.curve)
        exp_P = 3, 46

        assert P.x == exp_P[0]
        assert P.y == exp_P[1]

    def test_compute_y(self) -> None:
        Qyy = self.curve.compute_y(self.Qx)
        if Qyy is None:
            pytest.fail("Qxy should exist")

        y0, y1 = Qyy

        Q0 = Point(self.Qx, y0, self.curve)
        assert Q0.on_curve()

        Q1 = Point(self.Qx, y1, self.curve)
        assert Q1.on_curve()

        assert (y0 + y1) % self.curve.p == 0

    def test_order(self) -> None:
        assert self.curve.order == 96

    def test_sums_on_curve(self) -> None:
        c = self.curve

        y = c.compute_y(self.Px)
        if not y:
            pytest.fail("failed to compute Py")
        else:
            Py = y[0]

        y = c.compute_y(self.Qx)
        if not y:
            pytest.fail("failed to compute Qy")
        else:
            Qy = y[0]

        P = Point(self.Px, Py, c)
        Q = Point(self.Qx, Qy, c)

        PpQ = P.add(Q)
        assert PpQ.on_curve()

        P2 = P.double()
        assert P2.on_curve()

    def test_generator(self) -> None:
        assert self.G.x == 146
        assert self.G.y == 131
        assert self.G.is_zero is False

        assert self.G.on_curve() is True

        for d in range(2, self.curve.order):
            dG = self.G.scaler_multiply(d)
            assert dG.on_curve()

    def test_double(self) -> None:

        G2 = self.G.double()
        assert G2.x, G2.y == (8, 174)

        G4 = G2.double()
        assert G4.x, G4.y == (4, 96)

    def test_doubling_only(self) -> None:

        d = 2
        while d < self.curve.order:
            x, y = self.sage_vectors[d]
            dG = self.G.scaler_multiply(d)
            assert dG.x == x
            assert dG.y == y

            d = d ** 2

    def test_scaler_sage_data(self) -> None:
        for d in self.sage_vectors:
            x, y = self.sage_vectors[d]
            dG = self.G.scaler_multiply(d)
            assert dG.x == x
            assert dG.y == y

    def test_scaler_multipy(self) -> None:
        PaI = self.curve.PAI
        order = self.curve.order
        oG = self.G.scaler_multiply(order)
        assert oG == PaI  # f'order ({order} G = {oG}'
        assert self.G == self.G.scaler_multiply(1)

        G1 = self.G.scaler_multiply(order + 1)
        assert G1 == self.G

    def test_pai(self) -> None:
        c = self.curve
        PaI = c.PAI
        P = Point(self.Px, self.Py, c)
        negP = -P

        assert PaI.is_zero
        assert PaI + P == P
        assert P + PaI == P
        assert P - P == PaI
        assert negP + P == PaI

    def test_point_validation(self) -> None:
        with pytest.raises(ValueError):
            Point(self.Px, self.Py + 1, self.curve)


def test_curve_validation() -> None:
    with pytest.raises(ValueError):
        Curve(2, 3, p=Modulus(31 * 73))

    with pytest.raises(ValueError):
        Curve(2, 3, p=Modulus(5))


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
