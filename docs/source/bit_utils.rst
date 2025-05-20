.. include:: ../common/unsafe.rst

Utility functions
=================

.. py:module:: toy_crypto.bit_utils
    :synopsis: Various utilities for manipulationg bit-like things

    This module is imported with:

        import toy_crypto.bit-like_utils

.. currentmodule:: toy_crypto.bit_utils

.. autofunction:: bits

:func:`~toy_crypto.bit_utils.bits` is used by
:func:`~toy_crypto.ec.Point.scaler_multiply`
and would be used by modular exponentiation if I had included that.

>>> from toy_crypto.bit_utils import bits
>>> list(bits(13))
[1, 0, 1, 1]


.. autofunction:: hamming_distance

Let's illustrate with an `example from Cryptopals <https://cryptopals.com/sets/1/challenges/6>`__.

>>> from toy_crypto.bit_utils import hamming_distance
>>> s1 = b"this is a test"
>>> s2 = b"wokka wokka!!!"
>>> hamming_distance(s1, s2)
37
