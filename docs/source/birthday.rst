.. include:: ../common/unsafe.rst

Birthday Paradox Computations
================================

This module is imported with::

    import toy_crypto.birthday

.. currentmodule:: toy_crypto.birthday

The classic Birthday Paradox example is to estimate the number of individuals (whose birthdays are uniformly distributed among 365 days of the year) for there to be at least a 0.5 probability of there being at least one pair of individuals who share the same birthday.

The function that returns a propbably is named :func:`P`, and the one that returns a quantile is named :func:`Q`.
This follows the pattern of R's ``qbirthday`` and ``pbirthday``.

.. testcode::

    from toy_crypto import birthday

    computed_n = birthday.Q(0.5, 367)
    print(computed_n)

.. testoutput::

    23
        
Birthday computations are useful for computing collision probabilites.
Suppose you had a hash function (truncated to ) returning 32 bit hashes
and you wished to know the probability of a collision if you hashed ten thousand items.

.. testcode::

    from toy_crypto import birthday
    from math import isclose

    n = 10_000
    c = 2 ** 32

    p = birthday.P(n, c)
    assert isclose(p,  0.011574013876)


The :mod:`birthday` functions
------------------------------

.. automodule:: toy_crypto.birthday
    :synopsis: Birthday problem computations
    :members:
