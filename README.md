# Toy cryptographic utilities

This is almost certainly not the package you are looking for.

The material here is meant for learning purposes only, often my own learning.
Do not use it for anything else. And if you do, understand that it focuses on what
I am trying to illustrate or learn. It may not always be correct.

- If you want to use cryptographic tools in Python use [pyca].
- If you want to play with some of the mathematics of some things underlying Cryptography in
a Python-like environment use [SageMath].

[pyca]: https://cryptography.io
[SageMath]: https://doc.sagemath.org/

## Table of Contents

- [Toy cryptographic utilities](#toy-cryptographic-utilities)
  - [Table of Contents](#table-of-contents)
  - [Motivation](#motivation)
  - [Installation](#installation)
    - [If you must](#if-you-must)
  - [License](#license)

## Motivation

As I said above, this is almost certainly not the package you are looking for. Instead, [pyca] or [SageMath] will better suite your needs.

I wanted to have access to something that behaved a bit like SageMath's `factor()` without having do everything in Sage. If the sagemath-standard experimental package were less experimental, I wouldn't have needed to do this.

Note that my implementations of things like `factor()` or `is_square()` are not really optimized, and may fail in odd ways for very large numbers. These are quick and dirty substitutes that I hope will work well enough for numbers less than 2^64.

## Installation

Don't. This is not being maintained for general use.

### If you must

Installing this may create conflicts with anything else called math_utils, including the package by that name on PyPi

1. Clone this repository
2. In the repository folder use `pip install .`

## License

`math-utils` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
