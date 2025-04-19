.. include:: ../common/unsafe.rst

Sieve of Eratosthenes
======================

.. py:module:: toy_crypto.sieve
    :synopsis: Multiple implementataions for the Sieve of Eratosthenes

This module is imported with::

    import toy_crypto.sieve

The module contains classes for the factorization of numbers and for creating a sieve of Eratosthenes.

Why three separate implementations?
------------------------------------

It is reasonable to wonder why I have three distinct implementations.
There are reasons, but first let me give an overview of the major differences.

- The :class:`Sieve` class

    This uses the bitarray_ package underlyingly.
    It is by far the most time and memory efficient of the implemenations here.
    The bitarray_ package is written in C,
    and as a consequence it cannot be installed in certain environments.

The concrete classes
-----------------------

- The :class:`SetSieve` class

   This is a pure Python implementation that uses :py:class:`set` when creating the sieve.
   This consumes a lot of memmory.
   For a brief time during initialization there will be a set with all integers from 2 through n.
   The set will rapidly have elements removed from it,
   but the end results will still contain all of the primes as Python integers.

- The :class:`IntSieve` class

    This is also a pure Python implementation that uses a Python integer as the sieve and uses bit twidling when creating the sieve. This makes it memory efficient, but it is excruciatingly slow.


The :protocol:`Sievish` Protocol
----------------------------------
.. autoprotocol:: Sievish

The :class:`Sieve` class
---------------------------

.. autoclass:: Sieve
    :class-doc-from: both
    :members:


The :class:`SetSieve` class
---------------------------

.. autoclass:: SetSieve
    :class-doc-from: both
    :members:


The :class:`IntSieve` class
---------------------------

.. autoclass:: IntSieve
    :class-doc-from: both
    :members:





   
