.. include:: /../common/unsafe.rst

Utility functions
##################

.. py:module:: toy_crypto.utils
    :synopsis: Various utilities

    This module is imported with:

        import toy_crypto.utils

.. caution::

    Many libraries will have a module named `utils`, it is therefore
    unwise to do anything like

    .. code-block:: python

        # This is unwise
        from toy_crypto import utils

    as you might later find yourself in trouble not knowing
    whose ``utils`` are being referred to.


.. currentmodule:: toy_crypto.utils


.. autofunction:: digit_count

Coding this is a math problem, not a string representation problem.
Ideally the solution would be to use

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

.. autofunction:: next_power2

This is yet another function where talking a logarithm (base 2 this time)
would be the mathematically nice way to do things,

..   math:: p = \lceil \log_2(n) \rceil

but because we may want to use this with large numbers,
we have to worry floating point precision.

Because we are dealing with base 2,
we can do all of our multiplications and and divisions by powers of 2
using bit shifts. I am not sure how Pythonic that leaves things.

.. autofunction:: nearest_multiple

xor
===========

The :func:`utils.xor` and the class :class:`utils.Xor` provide utilities for xoring strings of bytes together. There is some asymmetry between the two arguments. The ``message`` can be an :py:class:`collections.abc.Iterator` as well as :py:class:`bytes`. The ``pad`` arguement on the other hand, is expected to be :py:class:`bytes` only (in this version.) The ``pad`` argument is will be repeated if it is shorter than the message.

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
===================================

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

Simple frozen bi-directional mapping
=====================================

For the :func:`Rsa129.encode` and :func:`Rsa129.decode`,
as well as for methods in the :class:`toy_crypto.vigenere.Alphabet`,
I found myself needing to look up the index of a character within a string.

I very strongly recommend that people use the outstanding
`bidict library <https://bidict.readthedocs.io/en/main/>`__
library instead of this.
I include my own, inferior version, simply because I wanted to reduce
dependencies.


>>> from toy_crypto.utils import FrozenBidict
>>> bi_mapping = FrozenBidict("ABCDEF")
>>> bi_mapping[2]
'C'
>>> bi_mapping.inverse['C']
2

This also can be initialized with a dictionary as long as the values in the
the dictionary are hashable.

>>> d = { "eggs": "ok", "bacon": "yummy", "SPAM": "essential"}
>>> tastes = FrozenBidict(d)
>>> tastes["bacon"]
'yummy'
>>> tastes.inverse["essential"]
'SPAM'

The :class:`FrozenBidict` is type parameterized,
with types representing the forward direction of the mapping, 
so the annotated versions of the above would be 

..  code-block:: python

    bi_mapping: FrozenBidict[int, str] = FrozenBidict("ABCDEF")
    tastes: FrozenBidict[str, str] = FrozenBidict(d)


.. autoclass:: FrozenBidict
    :members:

Find zero
==========

There are excellent equation and function solvers available in Python.
This is not one of them.

This was built explicitly has a helper function for the
:func:`~toy_crypto.birthday.quantile` function in the :mod:`birthday` module.
As such it assumes that

- The the input function, :math:`f(n)`, is non-decreasing in *n*;

- :math:`f: \mathbb{Z} \to \mathbb{R}`,
  or in Python has the type signature ``def f(n: int) -> float``;

- You want the least *n* for which :math:`f(n) \geq 0`
  even though :math:`f(n -1)` might be closer to 0;

- You don't mind using an embarrassingly kludgy implementation
  because for some reason I struggled with what should be a simple
  piece of code.

.. autofunction:: find_zero

Example
---------

Let's take :math:`f(n) = n^3 - 40` as an example.
It is non-decreasing and has a real zero at
:math:`\sqrt[3]{40} \approx 3.42`.
The smallest integer equal to or greater than that is 4.

.. doctest::

    >>> from toy_crypto.utils import find_zero
    >>> find_zero(lambda n: n ** 3 - 40)
    4

Once again, note that a proper solver would have been able to solve this
analytically, without resorting to a binary search or restricting to
non-decreasing functions only.
But this root finder is built to be just good enough for the
specific need in :func:`toy_crypto.birthday.quantile`.
