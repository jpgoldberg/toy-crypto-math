.. include:: ../common/unsafe.rst

Utility functions
=================

.. py:module:: toy_crypto.utils
    :synopsis: Various utilities

    This module is imported with:

        import toy_crypto.utils

.. currentmodule:: toy_crypto.utils


.. autofunction:: digit_count

Coding this is a math problem, not a string representation problem.
Idetally the solution would be to use

..  math:: d = \lfloor\log_b \| x \| + 1\rfloor

but that leads to erroneous results due to the precision limitations
of :py:func:`math.log`.

>>> from toy_crypto.utils import digit_count
>>> digit_count(999)
3
>>> digit_count(1000)
4
>>> digit_count(1001)
4
>>> digit_count(9999999999999998779999999999999999999999999999999999999999999)
61
>>> digit_count(9999999999999999999999999999999999999999999999999999999999999)
61
>>> digit_count(10000000000000000000000000000000000000000000000000000000000000)
62
>>> digit_count(0)
1
>>> digit_count(-10_000)
5

.. autofunction:: lsb_to_msb

:func:`~toy_crypto.utils.lsb_to_msb` is used by
:func:`~toy_crypto.ec.Point.scaler_multiply` and would be used by modular exponentiation
for implementations of those that leak the bits of the scalar (or exponent)
through side channels. 

>>> from toy_crypto.utils import lsb_to_msb
>>> list(lsb_to_msb(13))
[1, 0, 1, 1]


.. autofunction:: hamming_distance

Let's illustrate with an `example from Cryptopals <https://cryptopals.com/sets/1/challenges/6>`__.

>>> from toy_crypto.utils import hamming_distance
>>> s1 = b"this is a test"
>>> s2 = b"wokka wokka!!!"
>>> hamming_distance(s1, s2)
37


xor
-----

The :func:`utils.xor` and the class :class:`utils.Xor` provide utilities for xoring strings of bytes together. There is some assymetry between the two arguments. The ``message`` can be an :py:class:`collections.abc.Iterator` as well as :py:class:`bytes`. The ``pad`` arguement on the other hand, is expected to be :py:class:`bytes` only (in this version.) The ``pad`` argument is will be repeated if it is shorter than the message.

.. warning::

    The :type:`~toy_crypto.types.Byte` type is just a type alias for :py:class:`int`. There is no run time nor type checking mechanism that prevents you from passing an ``Iterator[Byte]`` message that contains integers outside of the range that would be expected for a byte.
    If you do so, bad things will happen. If you are lucky some exception from the bowels of Python will be raised in a way that will help you identify the error. If you are unlucky, you will silently get garbage results.

.. autoclass:: Xor
    :class-doc-from: both
    :members:

.. autofunction:: xor

>>> from toy_crypto.utils import xor
>>> message = b"Attack at dawn!"
>>> pad = bytes(10) + bytes.fromhex("00 14 04 05 00")
>>> modified_message = xor(message, pad)
>>> modified_message
b'Attack at dusk!'


Encodings for the RSA 129 challenge
-------------------------------------

When the RSA 129 challenge was first published in *Scientific American* in 1979
it used its own encoding scheme between text and integers.
This class provides an encoder and decoder for that scheme.

.. autoclass:: Rsa129
    :members: