# Toy cryptographic utilities

[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v0.json)](https://docs.astral.sh/ruff/)
[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://hatch.pypa.io/latest/)
[![License: MIT](https://img.shields.io/badge/license-MIT-C06524)](https://github.com/jpgoldberg/toy-crypto-math/blob/main/LICENSE.txt)

----


This is (almost certainly) not the package you are looking for.

The material here is meant for learning purposes only, often my own learning.
Do not use it for anything else. And if you do, understand that it focuses on what
I am trying to illustrate or learn.
It may not always be correct, and it is not coded with safely in mind.

- Use [pyca] if you need to use cryptographic tools in Python.
- Use [SageMath], [sympy], or [primefac] if you want to play with some of the mathematics of some things underlying Cryptography in
a Python-like environment.

[pyca]: https://cryptography.io
[SageMath]: https://doc.sagemath.org/
[sympy]: https://www.sympy.org/en/
[primefac]: https://pypi.org/project/primefac/
[PyPi]: https://pypi.org/

## Table of Contents

- [Toy cryptographic utilities](#toy-cryptographic-utilities)
  - [Table of Contents](#table-of-contents)
  - [Motivation](#motivation)
  - [Installation](#installation)
    - [If you must](#if-you-must)
  - [Usage](#usage)
  - [License](#license)

## Motivation

This package is almost certainly not the package you are looking for.
Instead, [pyca] or [SageMath] will better suite your needs.
I created it to meet a number of my own idiosyncratic  needs.

- I don't have the flexibility of Python version that I may want when using [SageMath].

  For example, I want to have access to something that behaves a bit like SageMath's `factor()`
  or the ability to play with elliptic curves without having do everything in Sage.
  Perhaps when [sagemath-standard](https://pypi.org/project/sagemath-standard/) quickly becomes available for the latest Python versions, I won't need to have my own (failable and incomplete) pure Python substitutes for some things I need.

- I sometimes talk about these algorithms for teaching purposes. Having pure Python versions allows me to present these.

  Proper cryptographic packages, like [pyca],

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

  I also want them to be _reproducible_, which is why I am making this public.

## Installation

Don't. If you need to do cryptography in Python use [pyca].

### If you must

Once I've published this to [PyPi], you will be able to install it with

```console
pip install toycrypto
```

Until this is released on PyPi, you will just have to install from this source.

## Usage

This is erratically documented at best, a combination of `pydoc` and reading the source it what you will need.

The import namespace is `toy_crypto`

An example might be something like this,
using the `factor` function from the Number Theory (nt) module.

```python
from toy_crypto.nt import factor

c = 9159288649
f = factor(c)

assert f == [(11, 2), (5483, 1), (104243, 1)]
assert str(f) == '11^2 * 5483 * 104243'
assert f.n == c
assert f.phi == 62860010840
```

## License

`toy-crypto-math` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
