.. toycrypto documentation master file, created by
   sphinx-quickstart on Mon Oct 14 13:01:10 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. include:: ../common/unsafe.rst

Toy cryptographic functions and utilities
==========================================

Some toy (unsafe for actual use) cryptography related utilites.

Installation
-------------

Remember that nothing here is built to be used for security purposes,
but if you must:

.. installation:: toycrypto
    :pypi:
    :github: main


Import names
------------

Once installed, the modules are imported under ``toy_crypto``.
For example, Number Theory module would be imported with ``import toy_crypto.nt``.


>>> from toy_crypto.nt import factor
>>> n = 69159288649
>>> factorization = factor(n)
>>> factorization.data
[(11, 2), (5483, 1), (104243, 1)]
>>> str(factorization)
'11^2 * 5483 * 104243'
>>> factorization.n == n
True
>>> factorization.phi
62860010840

Note again that the `SageMath Factorization class <https://doc.sagemath.org/html/en/reference/structure/sage/structure/factorization.html>`_ is far more efficient and general than what exists in this toy cryptography module.

Table of Contents 
------------------

.. toctree::
  :maxdepth: 3

  motivation
  utils
  bit_utils
  nt
  sieve
  rsa
  ec
  rand
  games
  birthday
  types
  vigenere
  bibliography
   