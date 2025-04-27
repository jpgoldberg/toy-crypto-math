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

- The :class:`SetSieve` class

   This is a pure Python implementation that uses :py:class:`set` when creating the sieve.
   This consumes a lot of memmory.
   For a brief time during initialization there will be a set with all integers from 2 through n.
   The set will rapidly have elements removed from it,
   but the end results will still contain all of the primes as Python integers.

- The :class:`IntSieve` class

    This is also a pure Python implementation that uses a Python integer as the sieve and uses bit twidling when creating the sieve. This makes it memory efficient, but it is excruciatingly slow.


.. figure:: images/all_data.png
    :alt: Graph showing that IntSieve creation time is really slow

    Time it takes in seconds for sieves of various sizes from 100 to 100000
    to be created by the different classes.

The algorithm
---------------

The algoritm for creating the sieve is the same for all three classes
but has fiddly differences due to how the seive is represented.
This, pared down and modified so as to work all by itself,
version from the :class:`SetSieve` is probably the most
readable.

.. testcode::

    from math import isqrt

    def make_sieve(n: int) -> list[int]:

        # This is where the heavy memory consumption comes in.
        sieve = set(range(2, n + 1))

        # We only need to go up to and including the square root of n,
        # remove all non-primes above that square-root =< n.
        for p in range(2, isqrt(n) + 1):
            if p in sieve:
                # Because we are going through sieve in numeric order
                # we know that multiples of anything less than p have
                # already been removed, so p is prime.
                # Our job is to now remove multiples of p
                # higher up in the sieve.
                for m in range(p + p, n + 1, p):
                    sieve.discard(m)

        return sorted(sieve)


>>> sieve100 = make_sieve(100)
>>> len(sieve100)
25

>>> sieve100[:5]
[2, 3, 5, 7, 11]

>>> sieve100[-5:]
[73, 79, 83, 89, 97]


The :protocol:`Sievish` Protocol
----------------------------------
.. autoprotocol:: Sievish

The concrete classes
-----------------------


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





   
