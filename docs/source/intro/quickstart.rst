
.. include:: /../common/unsafe.rst

Installing & Importing
=======================

Installation
-------------

Remember that nothing here is built to be used for security purposes,
but if you must:

..
  Until https://github.com/sphinx-toolbox/sphinx-toolbox/issues/190 is resolved
  I will not be using "sphinx_toolbox.installation",

.. 
  installation:: toycrypto
    :pypi:
    :github: main

From pypi_ for the latest *released* version::

    python3 -m pip install toycrypto --user

From GitHub for the head of the main branch::

    python3 -m pip install git+https://github.com/jpgoldberg/toy-crypto-math@main --user

Note that the major version number is 0. Things here may change in breaking ways.
    
Dependencies
------------

|project| can operate in pure Python environments
although some *optional* third party dependencies may
non-Python bindings.

The only required depedency is primefac_, which many utilities here wrap.
Though I might change that to SymPy_, now that I have learned it is pure python.

bitarray_ is an optional third party dependency that involves C bindings.

Import names
------------

Once installed, the modules are imported under ``toy_crypto``.
For example, :mod:`Number Theory module <nt>`
would be imported with ``import toy_crypto.nt``.


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
