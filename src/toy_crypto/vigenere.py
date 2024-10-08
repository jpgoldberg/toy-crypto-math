"""Vigenère: For demonstration use."""

from collections.abc import Sequence
from itertools import repeat
from typing import Any


class Alphabet:
    """An alphabet.

    This does not check if the alphabet is sensible. In particular, you may get
    very peculiar results if the alphabet contains duplicate elements.
    """

    default_alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def __init__(self, alphabet: str | None = None):
        """This does not check if the alphabet is sensible. In particular, you
        may get  very peculiar results if the alphabet contains duplicate
        elements.
        """

        if alphabet is None:
            alphabet = self.default_alphabet

        if not isinstance(alphabet, Sequence):
            raise TypeError("alphabet must be a Sequence")
        self.alphabet = alphabet

        self.modulus = len(self.alphabet)

        # Set up char to index table
        self.abc2idx: dict[str, int] = {
            c: i for i, c in enumerate(self.alphabet)
        }

    # We will want to use 'in' for Alphabet instances
    def __contains__(self, item: Any) -> bool:
        return item in self.alphabet

    # annoyingly, the type str is also used for single character strings
    # add, inverse, subtract all deal with single characters
    def add(self, a: str, b: str) -> str:
        """Returns the modular sum of two characters."""
        if a not in self or b not in self:
            raise ValueError("argument not an element")
        idx = (self.abc2idx[a] + self.abc2idx[b]) % self.modulus
        return self.alphabet[idx]

    def inverse(self, c: str) -> str:
        """Returns the additive inverse of character c"""
        if c not in self:
            raise ValueError("argument not an element")
        idx = self.modulus - self.abc2idx[c]
        return self.alphabet[idx]

    def subtract(self, a: str, b: str) -> str:
        """Returns the character corresponding to a - b."""
        return self.add(a, self.inverse(b))


class Cipher:
    """A Vigenère Cipher is a key and an alphabet."""

    def __init__(self, key: str, alphabet: Alphabet | str | None = None):
        if isinstance(alphabet, Alphabet):
            self.alphabet = alphabet
        else:
            self.alphabet = Alphabet(alphabet)

        if not key:
            raise ValueError("key must not be empty")

        if any([k not in self.alphabet for k in key]):
            raise ValueError(
                "key must be comprised of characters in the alphabet"
            )

        self.key = key

    def crypt(self, text: str, mode: str) -> str:
        """{en,de}crypts text depending on mode"""

        match mode:
            case "encrypt":
                operation = self.alphabet.add
            case "decrypt":
                operation = self.alphabet.subtract
            case _:
                raise ValueError("mode must be 'encrypt' or 'decrypt")

        # TODO: Generalize this for streaming input and output
        output: list[str] = []

        for c, k in zip(text, repeat(self.key)):
            if c not in self.alphabet:
                result = c
            else:
                result = operation(c, k)

            output.append(result)

        return str(output)

    def encrypt(self, plaintext: str) -> str:
        """Returns ciphertext."""

        return self.crypt(plaintext, mode="encrypt")

    def decrypt(self, ciphertext: str) -> str:
        """Returns plaintext."""

        return self.crypt(ciphertext, mode="decrypt")
