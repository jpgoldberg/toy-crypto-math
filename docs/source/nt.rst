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

The :class:`Sieve` class
---------------------------

.. autoclass:: toy_crypto.nt.Sieve
    :class-doc-from: both
    :members:

Other functions
----------------

.. automodule:: toy_crypto.nt
    :members: gcd, lcm, egcd, is_square, mod_sqrt
   
   
