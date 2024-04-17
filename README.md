# A personal collection of math utilities I use

Although this is a public repository for those who might wish to poke around in it,
it is not being maintained for public consumption. And it is not being published to PyPi.

## Table of Contents

- [A personal collection of math utilities I use](#a-personal-collection-of-math-utilities-i-use)
  - [Table of Contents](#table-of-contents)
  - [Motivation](#motivation)
  - [Installation](#installation)
    - [If you must](#if-you-must)
  - [License](#license)

## Motivation

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
