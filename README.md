# Toy cryptographic utilities

This is almost certainly not the package you are looking for.

The material here is meant for learning purposes only, often my own learning.
Do not use it for anything else. And if you do, understand that it focuses on what
I am trying to illustrate or learn. It may not always be correct.

- If you want to use cryptographic tools in Python use [pyca].
- If you want to play with some of the mathematics of some things underlying Cryptography in
a Python-like environment use [SageMath], [sympy], or [primefac].

[pyca]: https://cryptography.io
[SageMath]: https://doc.sagemath.org/
[sympy]: https://www.sympy.org/en/
[primefac]: https://pypi.org/project/primefac/

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

  Perhaps when [sagemath-standard](https://pypi.org/project/sagemath-standard/) quickly becomes available for the latest Python versions, I won't need to have my own (failable and incomplete) pure Python substitutes for some things I need.

- I sometimes talk about these algorithms for teaching purposes. Having pure Python versions allows me to present these.

- Some of these I created or copied for my own learning purposes.

- I have a number of "good enough" (for my purposes) implementations of things that I want to reuse.

  For example, Birthday collision calculations are things I occasionally want, and I don't want to hunt for wherever I have something like that written or rewrite it yet again.
  Likewise, I wouldn't be surprised if I'm written the extended GCD algorithm more than a dozen times
  (not all in Python), and so would like to have at least the Python version in one place

- I want to use cryptographic examples in Jupyter Notebooks.

  Proper cryptographic packages, like [pyca],

  - Correctly obscure the lower level primitives I may wish to exhibit;
  - Correctly prevent use of unsafe parameters such as small keys;
  - Correctly involve a lot of abstractions in the calls to the concealed primitives.

  Those features, essential for something to be used, are not great for expository discussion.

I wanted to have access to something that behaved a bit like SageMath's `factor()` without having do everything in Sage. If the `sagemath-standard` experimental package were less experimental, I wouldn't have needed to do this.

Note that my implementations of things like `factor()` or `is_square()` are not really optimized, and may fail in odd ways for very large numbers. These are quick and dirty substitutes that I hope will work well enough for numbers less than 2^64.

## Installation

Don't. This is not being maintained for general use. I may make substantial changes between updates.

### If you must

[hatchling]: https://pypi.org/project/hatchling/ "hatchling: Python build backend"

1. Have working Python setup.
2. Clone this repository.
3. Install the development requirements from `dev-requirements.txt`, that can be done with something like

   ```command
   pip install -r dev-requirements.txt
   ```

4. For testing, you will also need to dependencies from `requirements.txt`.
5. Build with [hatchling]. (There are other ways to do it, but this is what works for me)

   ```command
   hatch build
   ```

6. That will create a `.whl` file in the `./dist`, with a name like `toycrypto-VERSION-NUMBER-py3-none-any.whl`. Use `pip install dist/toycrypto-VERSION-NUMBER-py3-none-any.whl`, but with the appropriate version number.


## Usage

this is erratically documented at best, a combination of `pydoc` and reading the source it what you will need.
But an example might be something like this,
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
