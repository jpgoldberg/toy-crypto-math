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

.. doctest::

    >>> from toy_crypto import nt
    >>> pseudo_prime = 174763 * 199729 * 274627  # This is not prime
    >>> print(f"{pseudo_prime} isn't prime.")
    9585921133193329 isn't prime.
    >>> ft_result = nt.fermat_test(pseudo_prime)
    >>> ft_message = f"Fermat test: {"probably prime" if ft_result else "composite"}.}
    >>> print(ft_message) # doctest: +ELLIPSES
    Fermat test: ....


That will *usually* report “Fermat test: probably prime.”
That would be incorrect.
But if any of the randomly chosen bases are ever multiples of the factors
of our pseudo prime, then the Fermat test will correctly identify
it as composite.

The Rabin-Miller test, which is used in :func:`probably_prime` will
do better.

.. doctest::

    >>> rb_result = nt.probably_prime(9585921133193329)
    >>> rb_message = f"Miller-Rabin test: {"probably prime" if ft_result else "composite"}.}
    >>> print(rb_message)  # doctest: +ELLIPSES
    Miller-Rabin test: ....

which should almost always identify our pseudo prime as composite.



.. admonition:: *Last* versus *Little*

    - Fermat's *Last* Theorem is famous because Fermat never proved it.
    - Fermat never proved the *Little* theorem either.
    - The *Little* theorem was proved by Leibniz around 1683.
    - The *Last* theorem was proved by Andrew Wiles in 1994.
    - Unlike Fermat's *Last* Theorem, the *Little* Theorem is enormously useful.


.. autofunction:: fermat_test

.. autofunction:: probably_prime

.. autofunction:: get_prime

Wrapping from primefac_
------------------------

Functions here wrap functions from the primefac_ Python package.
Note that the wrapping is not completely transparent in some cases.
That is, the interface and behavior may differ.

.. autofunction:: factor

.. autofunction:: mod_sqrt

.. autofunction:: is_square

.. autofunction:: isqrt

.. autofunction:: isprime

The :class:`FactorList` class
------------------------------

Some of the methods here are meant to mimic
a small part of what we see in SageMath's Factorization class,
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




Additional functions
========================

Before Python gave us an easy way to compute modular inverses,
the Extended Euclidean algorithm was what I used.
Although it is no longer called in :func:`modinv`,
I am keeping it around.

.. autofunction:: egcd

The :class:`Modulus` type and
its ``typing.TypeGuard``, :func:`is_modulus`,
are not very well thought out.
They may disappear if I ever get around to overhauling the
:mod:`toy_crypto.ec` module,
or at least be put somewhere else.

.. autoclass:: Modulus

.. autofunction:: is_modulus

Wrapping some :py:mod:`math`
------------------------------

There are functions which either weren't part of the Python standard library at the time I started putting some things together, or I wasn't aware of their existence, or I just wanted to write for myself some reason or the other.

But now, at least in this module, I wrap those. 

.. autofunction:: gcd

.. autofunction:: lcm

.. autofunction:: modinv



