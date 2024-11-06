.. include:: ../common/unsafe.rst

Elliptic curves
================

.. py:module:: toy_crypto.ec
    :synopsis: Simple elliptic curves

This are imported with::

    import toy_crypto.ec

.. currentmodule:: toy_crypto.ec

I wrote this for the sole purposes of

1. Providing a working context to illustrate the double-and-add algorithm in the :py:meth:`Point.scaler_multiply` method.
2. Doing calculations over floats that I could use for diagrams.

And I have since removed the code for (2).

.. testcode::

    from toy_crypto.ec import Curve
    from toy_crypto.nt import Modulus

    
    # Example curve from Serious Cryptography

    curve = Curve(-4, 0, 191)
    assert str(curve) == "y^2 = x^3 - 4x + 0 (mod 191)"

    # set a generator (base-point), G
    G = curve.point(146, 131)

    assert G.on_curve() is True

    five_G = G.scaler_multiply(5)
    assert five_G.x == 61
    assert five_G.y == 163



The :mod:`ec` classes
----------------------

.. autoclass:: Curve
    :class-doc-from: both
    :members:

.. autoclass:: Point
    :class-doc-from: both
    :members:
