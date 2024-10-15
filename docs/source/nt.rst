.. include:: ../common/unsafe.rst

Number Theory
==============

This are imported with::

    import toy_crypto.nt

The module contains classes for the factorization of numbers and for creating a sieve of Eratosthenes.

The :class:`FactorList` class
------------------------------

Some of the methods here are meant to mimic what we
see in SageMath's Factorization class,
but it only does so partially, and only for :py:class:`int`.
If you need something as reliable and
general and fast as SageMath's Factorization tools,
use SageMath_.

.. autoclass:: toy_crypto.nt.FactorList
    :class-doc-from: both
    :members:

.. autofunction:: toy_crypto.nt.factor
    :no-index:

The :class:`Sieve` class
---------------------------

.. autoclass:: toy_crypto.nt.Sieve
    :class-doc-from: both
    :members:

Functions
----------

.. autofunction:: toy_crypto.nt.egcd

.. autoclass:: toy_crypto.nt.Modulus

.. autofunction:: toy_crypto.nt.is_modulus


Wrapping some :py:mod:`math`
'''''''''''''''''''''''''''''

There are functions which either weren't part of the Python standard library at the time I started putting some things together, or I wasn't aware of their existence, or I just wanted to write for myself some reason or the other.

But now, at least in this module, I wrap those. 

.. automodule:: toy_crypto.nt
    :members: gcd, lcm, modinv

Wrapping from primefac_
'''''''''''''''''''''''''

Functions here wrap functions from the primefac_ Python package.
Note that the wrapping is not completely transparent in some cases.
That is the interface and behavior may differ.

.. automodule:: toy_crypto.nt
    :members: factor, is_square, mod_sqrt, isqrt, isprime
   
   
