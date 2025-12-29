.. include:: /../common/unsafe.rst

Birthday Paradox Computations
================================

This module is imported with::

    import toy_crypto.birthday

.. currentmodule:: toy_crypto.birthday

The classic :wikipedia:`Birthday problem` example is
to estimate the number of individuals
(whose birthdays are uniformly distributed among 365 days of the year)
for there to be at least a 0.5 probability of there being at least one pair of individuals who share the same birthday.

The function that returns a probability is named :func:`probability`,
and the one that returns a quantile is named :func:`quantile`.
This loosely follows the R conventions
[:cite:label:`RProject`]
as reflected in R's ``qbirthday`` and ``pbirthday`` functions.

.. testcode::

    from toy_crypto import birthday

    computed_n = birthday.quantile(0.5, 367)
    print(computed_n)

.. testoutput::

    23
        
Birthday computations are useful for computing collision probabilities.
Suppose you had a hash function (truncated to ) returning 32 bit hashes
and you wished to know the probability of a collision if you hashed ten thousand items.

.. testcode::

    from toy_crypto import birthday
    from math import isclose

    n = 10_000
    c = 2 ** 32

    p = birthday.probability(n, c)
    assert isclose(p,  0.011574013876)

This implementation is crafted to work for even larger numbers.
Suppose you wanted to know how many 128-bit tokens you would
need to generate to have a one in one-billion (10\ :sup:`-9`)
chance of a collision.

.. doctest::

    >>> import math
    >>> n = birthday.quantile(1e-9, 1 << 128)
    >>> math.isclose(n, 824963474453361)
    True


The :mod:`birthday` functions
------------------------------

.. automodule:: toy_crypto.birthday
    :synopsis: Birthday problem computations
    :members:

Notes on the implementation
------------------------------

It was not a simple matter for me to find or construct an algorithm that 
produces reasonable approximations in a reasonably efficient way for the
ranges of numbers I wished to consider.
Eventually I found the solution used by :cite:t:`RProject`
in `R's birthday.R source <https://github.com/wch/r-source/blob/trunk/src/library/stats/R/birthday.R>`__, which credits :cite:t:`DiaconisMosteller1989`.

That R code is the basis for some of the approximations, but as it stands
it is not suitable for the large values relevant for Cryptography.
So my code differs from the original R code in two substantive respects.

1. It allows use of the approximation in :func:`probability`
   even when the ``coincident`` parameter is 2.
2. After computing the approximate quantile in `:func:`quantile`
   this refines that through a binary search 
   (see :func:`toy_crypto.utils.find_zero`)
   instead of just talking single steps to the complete answer.

Both of those modifications allow us to perform birthday problem computations
with larger numbers.

