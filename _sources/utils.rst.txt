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
So a different approach is taken which correctly handles cases that
would otherwise fail.

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

Martin :cite:authors:`Gardner77:RSA` first reported the Rivest, Shamir, and Adleman (RSA) in :cite:year:`Gardner77:RSA`.
The examples and challenge described in it used an encoding scheme
between text and (large) integers.
This class provides an encoder and decoder for that scheme.

We will take the magic words, decrypted in
:cite:year:`AtkinsETAL1995:squeamish` by
:cite:authors:`AtkinsETAL1995:squeamish`
with the help of a large number of volunteers,
from that challenge for our example:


>>> from toy_crypto.utils import Rsa129
>>> decrypted = 200805001301070903002315180419000118050019172105011309190800151919090618010705
>>> Rsa129.decode(decrypted)
'THE MAGIC WORDS ARE SQUEAMISH OSSIFRAGE'

And we will use an example from :cite:p:`Gardner77:RSA`.

>>> latin_text = "ITS ALL GREEK TO ME"
>>> encoded = Rsa129.encode(latin_text)
>>> encoded
9201900011212000718050511002015001305
>>> assert Rsa129.decode(encoded) == latin_text


.. autoclass:: Rsa129
    :members: