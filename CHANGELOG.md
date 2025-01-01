# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

## 0.1.7 2025-01-01

### Changed

- `IndCpa` is now correctly called `IndEav`

## 0.1.6 2024-12-31

### Added

- `sec_games` module with symmetric IND-CPA game

### Changed

- birthday.Q uses simple approximation when p > MAX_BIRTHDAY_Q instead of raising exception

### Improved

- Improved test coverage for birthday module
- Documentation improvements

## 0.1.5 2024-11-30

### Changed

- `vigenere` now only works with `str`. If you want to do things with `bytes`, use `utils.xor`.

- Vigenère encryption and decryption no longer advance the key when passing through input that is not in the alphabet.
  
### Fixed

- Vigenère behavior on input not in alphabet is less incoherent than before, though perhaps it should be considered undefined.

- Sprinkled more `py.typed` files around so this really should get marked at typed now.

### Added

- `utils.hamming_distance()` is now a thing.
- `vigenere.probable_keysize()` is also now a thing.
- `utils.xor()` can take an Iterator[int] has a message, so the entire message does not need to be stored
- The `utils.Xor` class creates an Iterator of xoring a message and a pad.
  
### Improved

- `birthday` module now has a [documentation page](https://jpgoldberg.github.io/toy-crypto-math/birthday.html).
- `types` module now has a [documentation page](https://jpgoldberg.github.io/toy-crypto-math/types.html).

## 0.1.4 2024-11-06

### Changed

- keyword argument name `b` changed to "`base`" in `utils.digit_count`.

### Added

- Text encoder for the R129 challenge is exposed in `utils`.
  
  Previously this had just lived only in test routines.

### Fixed

- `utils.digit_count` Fixed bug that could yield incorrect results in close cases.
  
### Improved

- `rand` module now has a [documentation page](https://jpgoldberg.github.io/toy-crypto-math/rand.html).
- Improved error messages for some Type and Value Errors.
- Made it harder to accidentally mutate things in the `ec` class that shouldn't be mutated.
- Improved documentation and test coverage for `utils` and `ec`.
- Improved documentation for the `rsa` module.
- Minor improvements to other documentation and docstrings

## 0.1.3 2024-10-17

### Added

- `py.typed` file. (This is the reason for the version bump.)

### Improved

- `ec` classes use `@property` instead of exposing some attributes directly.
- `ec` module now has a [documentation page]( https://jpgoldberg.github.io/toy-crypto-math/ec.html).
- This changelog is now in the proper location.
- This changelog is better formatted.

## 0.1.2 2024-10-15

### Added

- _Partial_ [documentation][docs].

### Improved

- Testing covers all supported Python versions (3.11, 3.12, 3.13)

## 0.1.1 2024-10-11

### Removed

- `redundent.prod()`. It was annoying type checkers and is, after all, redundant.

### Added

- `utils.xor()` function for xor-ing bytes with a pad.
- Explicit support for Python 3.13
- Github Actions for linting and testing

### Improved

- Conforms to some stronger lint checks
- Spelling in some code comments

## 0.1.0 - 2024-10-10

### Added

- First public release
  
[docs]: https://jpgoldberg.github.io/toy-crypto-math/
