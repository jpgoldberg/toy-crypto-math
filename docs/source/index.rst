.. toycrypto documentation master file, created by
   sphinx-quickstart on Mon Oct 14 13:01:10 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. include:: ../common/unsafe.rst

Toy cryptographic functions and utilities
==========================================

Some toy (unsafe for actual use) cryptography related utilites.

Installation
------------

Don't. If you need to do cryptography in Python use `pyca`_.

If you must
```````````

::

   pip install toycrypto

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

Modules 
-------

.. toctree::
   :maxdepth: 1
   :caption: Documented modules:

   utils
   nt
   rsa
   ec
   rand
   birthday
   types
   vigenere
   redundent
   

Motiviation
-----------

This package is almost certainly not the package you are looking for.
Instead, pyca_ or SageMath_ will better suite your needs.
I created it to meet a number of my own idiosyncratic  needs.

- I don't have the flexibility of Python version that I may want when using SageMath_.

  For example, I want to have access to something that behaves a bit like SageMath's ``factor()``
  or the ability to play with elliptic curves without having do everything in Sage.
  Perhaps when `sagemath-standard <https://pypi.org/project/sagemath-standard/>`_ quickly becomes available for the latest Python versions, I won't need to have my own (failable and incomplete) pure Python substitutes for some things I need.

- I sometimes talk about these algorithms for teaching purposes. Having pure Python versions allows me to present these.

  Proper cryptographic packages, like pyca_,

  - Correctly obscure the lower level primitives I may wish to exhibit;
  - Correctly prevent use of unsafe parameters such as small keys;
  - Correctly involve a lot of abstractions in the calls to the concealed primitives.

  Those features, essential for something to be used, are not great for expository discussion.

- Some of these I created or copied for my own learning purposes.

- I have a number of "good enough" (for my purposes) implementations of things that I want to reuse.

  For example, Birthday collision calculations are things I occasionally want, and I don't want to hunt for wherever I have something like that written or rewrite it yet again.
  Likewise, I wouldn't be surprised if I'm written the extended GCD algorithm more than a dozen times
  (not all in Python), and so would like to have at least the Python version in one place

- I want to use cryptographic examples in Jupyter Notebooks.

  I also want them to be *reproducible*, which is why I am making this public.

