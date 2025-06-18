.. include:: ../common/unsafe.rst

Number Theory
==============

.. py:module:: toy_crypto.nt
    :synopsis: Number theorertic utilities and integer factorization tools

This module is imported with::

    import toy_crypto.nt

The module contains classes for the factorization of numbers along this some utility functions.

The :class:`FactorList` class
------------------------------

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

Functions
----------

.. autofunction:: egcd

.. autoclass:: Modulus

.. autofunction:: is_modulus


Wrapping some :py:mod:`math`
'''''''''''''''''''''''''''''

There are functions which either weren't part of the Python standard library at the time I started putting some things together, or I wasn't aware of their existence, or I just wanted to write for myself some reason or the other.

But now, at least in this module, I wrap those. 

.. autofunction:: gcd

.. autofunction:: lcm

.. autofunction:: modinv



Wrapping from primefac_
'''''''''''''''''''''''''

Functions here wrap functions from the primefac_ Python package.
Note that the wrapping is not completely transparent in some cases.
That is, the interface and behavior may differ.

.. autofunction:: factor

.. autofunction:: mod_sqrt

.. autofunction:: is_square

.. autofunction:: isqrt

.. autofunction:: isprime
   
   
