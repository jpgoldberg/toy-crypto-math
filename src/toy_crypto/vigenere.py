"""Vigenère: For demonstration use."""

from collections.abc import Sequence
from itertools import cycle
from typing import Any, Optional, TypeAlias, Union

# Letter is meant to be a single character or byte, but this is not enforced.
Letter: TypeAlias = Union[str, bytes]
Letters: TypeAlias = Sequence[Letter]


class Alphabet_meta(type):
    def __init__(cls, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        cls._abc_caps_only = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

        # Printable 7 bit ASCI with space but excluding backlash. Shuffled.
        cls._abc_shuffled_printable = r"""JDi-Km9247oBEctS%Isxz{<;=W^fL,[Y3Mgd6HV(kR8:_CF"*')>|#~Xay!]N+1vnqTl/}j$A.@0b ZGe`UPhp?Ow&ru5Q"""

        cls._default_alphabet = cls._abc_caps_only

    @property
    def default_alphabet(cls) -> Letters:
        return cls._default_alphabet

    @property
    def abc_caps_only(cls) -> Letters:
        return cls._abc_caps_only

    @property
    def abc_printable(cls) -> Letters:
        return cls._abc_shuffled_printable


class Alphabet(metaclass=Alphabet_meta):
    """An alphabet.

    This does not check if the alphabet is sensible. In particular, you may get
    very peculiar results if the alphabet contains duplicate elements.

    Instances of this class are conventionally immutable.
    """

    def __init__(
        self,
        alphabet: Optional[Letters] = None,
        prebaked: Optional[str] = None,
    ):
        """This does not check if the alphabet is sensible. In particular, you
        may get  very peculiar results if the alphabet contains duplicate
        elements.
        """

        match (alphabet, prebaked):
            case (None, None) | (None, "default"):
                abc = Alphabet.default_alphabet
            case (None, "caps"):
                abc = Alphabet.abc_caps_only
            case (None, "printable"):
                abc = Alphabet.abc_printable
            case (None, _):
                raise ValueError("Unknown pre-baked alphabet")
            case (_, None):
                if not isinstance(alphabet, Sequence):
                    raise TypeError("alphabet must be a Sequence")
                abc = alphabet
            case (_, _):
                raise ValueError(
                    "Can't use both explicit and pre-baked alphabet"
                )

        self._alphabet = abc

        self._modulus = len(self._alphabet)

        # Set up char to index table
        self._abc2idx: dict[Letter, int] = {
            c: i for i, c in enumerate(self._alphabet)
        }

    @property
    def alphabet(self) -> Letters:
        return self._alphabet

    @property
    def modulus(self) -> int:
        return self._modulus

    @property
    def abc2idx(self) -> dict[Letter, int]:
        return self._abc2idx

    # We will want to use 'in' for Alphabet instances
    def __contains__(self, item: Any) -> bool:
        return item in self.alphabet

    # annoyingly, the type str is also used for single character strings
    # add, inverse, subtract all deal with single characters
    def add(self, a: Letter, b: Letter) -> Letter:
        """Returns the modular sum of two characters."""
        if a not in self or b not in self:
            raise ValueError("argument not an element")
        idx = (self.abc2idx[a] + self.abc2idx[b]) % self.modulus
        return self.alphabet[idx]

    def inverse(self, c: Letter) -> Letter:
        """Returns the additive inverse of character c"""
        if c not in self:
            raise ValueError("argument not an element")
        idx = (self.modulus - self.abc2idx[c]) % self.modulus
        return self.alphabet[idx]

    def subtract(self, a: Letter, b: Letter) -> Letter:
        """Returns the character corresponding to a - b."""
        return self.add(a, self.inverse(b))


class Cipher:
    """A Vigenère Cipher is a key and an alphabet."""

    def __init__(
        self, key: Letters, alphabet: Alphabet | Letters | None = None
    ):
        if isinstance(alphabet, Alphabet):
            abc = alphabet
        else:
            abc = Alphabet(alphabet)

        self._alphabet = abc

        if not key:
            raise ValueError("key must not be empty")

        if any([k not in self._alphabet for k in key]):
            raise ValueError(
                "key must be comprised of characters in the alphabet"
            )
        self._key: Letters = key

    @property
    def alphabet(self) -> Alphabet:
        return self._alphabet

    @property
    def key(self) -> Letters:
        return self._key

    def crypt(self, text: Letters, mode: str) -> Letters:
        """{en,de}crypts text depending on mode"""

        match mode:
            case "encrypt":
                operation = self.alphabet.add
            case "decrypt":
                operation = self.alphabet.subtract
            case _:
                raise ValueError("mode must be 'encrypt' or 'decrypt")

        # TODO: Generalize this for streaming input and output
        output: list[Letter] = []

        for c, k in zip(text, cycle(self.key)):
            if c not in self.alphabet:
                result = c
            else:
                result = operation(c, k)

            output.append(result)

        if isinstance(text, bytes):
            return b"".join(output)
        return "".join(output)  # type: ignore[arg-type]

    def encrypt(self, plaintext: Letters) -> Letters:
        """Returns ciphertext."""

        return self.crypt(plaintext, mode="encrypt")

    def decrypt(self, ciphertext: Letters) -> Letters:
        """Returns plaintext."""

        return self.crypt(ciphertext, mode="decrypt")
