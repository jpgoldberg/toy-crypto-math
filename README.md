# Toy cryptographic utilities

[![mypy status][type-badge]](https://mypy.readthedocs.io/en/stable/)
[![ruff status][lint-badge]](https://docs.astral.sh/ruff/)
[![pytest status][test-badge]](https://docs.pytest.org/en/stable/)
![Doctest status][doctest-badge]
[![PyPI](https://img.shields.io/pypi/v/toycrypto?label=pypi%20package)][published]
[![Documentation][doc-build-badge]][documentation]
[![License: MIT](https://img.shields.io/badge/license-MIT-C06524)](https://github.com/jpgoldberg/toy-crypto-math/blob/main/LICENSE.txt)

----

This is a collection of utilities that can be used for illustrating or
exploring some cryptographic concepts.
Although it includes implementations of some cryptographic algorithms,
these are **not secure** implementations.

See the [documentation] for use (or not) and [reasons why this exists](https://jpgoldberg.github.io/toy-crypto-math/why/).

Note that if you need to do cryptography in Python,
I recommend [pyca](https://cryptography.io/) or [PyNaCl](https://pynacl.readthedocs.io/en/latest/).
If you want tools to explore the algebraic and number theoretic constructs used in cryptography,
look at [SageMath](https://doc.sagemath.org/) or [SymPy](https://www.sympy.org/en/index.html).

[published]: https://pypi.org/project/toycrypto/ "toycrypto on PyPi"
[documentation]: https://jpgoldberg.github.io/toy-crypto-math/

[type-badge]: https://github.com/jpgoldberg/toy-crypto-math/actions/workflows/type-check.yml/badge.svg
[lint-badge]: https://github.com/jpgoldberg/toy-crypto-math/actions/workflows/lint.yml/badge.svg
[test-badge]: https://github.com/jpgoldberg/toy-crypto-math/actions/workflows/pytest.yml/badge.svg
[doctest-badge]: https://github.com/jpgoldberg/toy-crypto-math/actions/workflows/doctest.yml/badge.svg
[doc-build-badge]: https://github.com/jpgoldberg/toy-crypto-math/actions/workflows/gh-pages.yml/badge.svg
