.. include:: /../common/unsafe.rst

###############
Number Theory
###############

.. py:module:: toy_crypto.nt
    :synopsis: Number theoretic utilities and integer factorization tools

This module is imported with::

    import toy_crypto.nt

The module contains pure Python classes and functions for a handful of
integer math utilities. The SymPy_ ``ntheory`` module is almost certainly
going to have better versions of everything here.

.. _SymPy: https://www.sympy.org/

The :class:`FactorList` class
========================

Some of the methods here are meant to mimic what we
see in SageMath's Factorization class,
but it only does so partially, and only for :py:class:`int`.
If you need something as reliable and
general and fast as SageMath's Factorization tools,
use SageMath_.

The actual factoring is done by the primefac_ package.


.. autoclass:: FactorList
    :class-doc-from: both
    :members:

.. autofunction:: factor
    :no-index:


Prime testing and utilities
============================

In addition to what is present in this module :mod:`toy_crypto.sieve`
has various ways for creating and using prime sieves.
The :mod:`toy_crypto.rsa` module contains
:func:`toy_crypto.rsa.fips186_prime_gen` for generating
primes suitable for RSA keys.

The heart of most primality testing is
:wikipedia:`Fermat's Little Theorem`.
It tells us that if *p* is prime then
for all integers *a* such *a* is greater than 1 and less than *p*
that

.. math::
    
    a^{p-1} \equiv 1 \pmod p


.. note::

    It is very important to note that Fermat's Little Theorem
    doesn't say that that condition holds *only* of prime numbers;
    it just says that the condition holds of *every* prime number.
    There are numbers, for example if we pick
    *a* = 2 and *p* = 341, then
    :math:`2^{341 - 1} \equiv 1 \pmod{341}`
    even though 341 is not prime.

    Furthermore, there are composite numbers, such as 561, for which the condition holds no matter what value of *a* we pick.
    These are :wikipedia:`Carmichael number`\s.

.. code-block:: python 

    from toy_crypto import nt
    pseudo_prime = 41 * 61 * 101  # This is not prime
    reported_prime = nt.fermat_test(pseudo_prime)
    print(reported_prime)

That will *usually* report ``True``, which is incorrect.
But if the randomly chosen bases are ever multiples of the factors
of our pseudo prime, then the Fermat test will correctly identify
it as composite.
    


.. admonition:: *Last* versus *Little*

    - Fermat's *Last* Theorem is famous because Fermat never proved it.
    - Fermat never proved the *Little* theorem either.
    - The *Little* theorem was proved by Leibniz around 1683.
    - The *Last* theorem was proved by Andrew Wiles in 1994.
    - Unlike Fermat's *Last* Theorem, the *Little* Theorem is enormously useful.


.. autofunction:: fermat_test

.. autofunction:: probably_prime

.. autofunction:: get_prime

.. autoclass:: Modulus

.. autofunction:: is_modulus

Wrapping from primefac_
''''''''''''''''''''''''

Functions here wrap functions from the primefac_ Python package.
Note that the wrapping is not completely transparent in some cases.
That is, the interface and behavior may differ.

.. autofunction:: factor

.. autofunction:: mod_sqrt

.. autofunction:: is_square

.. autofunction:: isqrt

.. autofunction:: isprime


Functions
========================

.. autofunction:: egcd


Wrapping some :py:mod:`math`
------------------------------

There are functions which either weren't part of the Python standard library at the time I started putting some things together, or I wasn't aware of their existence, or I just wanted to write for myself some reason or the other.

But now, at least in this module, I wrap those. 

.. autofunction:: gcd

.. autofunction:: lcm

.. autofunction:: modinv



