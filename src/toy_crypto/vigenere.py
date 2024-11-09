from typing import Any, Optional, TypeAlias

Letter: TypeAlias = str
"""Intended to indicate a str of length 1"""


class Alphabet:
    """An alphabet.

    This does not check if the alphabet is sensible. In particular, you may get
    very peculiar results if the alphabet contains duplicate elements.

    Instances of this class are conventionally immutable.
    """

    CAPS_ONLY = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    """'A' through 'Z' in order."""

    # Printable 7 bit ASCI with space but excluding backslash. Shuffled.
    PRINTABLE = r"""JDi-Km9247oBEctS%Isxz{<;=W^fL,[Y3Mgd6HV(kR8:_CF"*')>|#~Xay!]N+1vnqTl/}j$A.@0b ZGe`UPhp?Ow&ru5Q"""
    """
    Printable 7-bit ASCII in a fixed scrambled order.

    It does not include the backslash character,
    and the scrambled order is hardcoded.
     """

    DEFAULT = CAPS_ONLY
    """CAPS_ONLY is the default."""

    def __init__(
        self,
        alphabet: Optional[str] = None,
        prebaked: Optional[str] = None,
    ):
        """This does not check if the alphabet is sensible. In particular, you
        may get  very peculiar results if the alphabet contains duplicate
        elements.
        """

        match (alphabet, prebaked):
            case (None, None) | (None, "default"):
                abc = self.DEFAULT
            case (None, "caps"):
                abc = self.CAPS_ONLY
            case (None, "printable"):
                abc = self.PRINTABLE
            case (None, _):
                raise ValueError("Unknown pre-baked alphabet")
            case (_, None):
                if not isinstance(alphabet, str):
                    raise TypeError("alphabet must be a string")
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
    def alphabet(self) -> str:
        """The underlying alphabet."""
        return self._alphabet

    @property
    def modulus(self) -> int:
        """The modulus."""
        return self._modulus

    @property
    def abc2idx(self) -> dict[Letter, int]:
        """Dictionary of letter to position in the alphabet."""
        return self._abc2idx

    # We will want to use 'in' for Alphabet instances
    def __contains__(self, item: Any) -> bool:
        """
        Allows the 'in' and 'not in' operators.

        So if `abc` is an Alphabet, ``'Z' in abc`` is well defined.
        """
        return item in self.alphabet

    def __getitem__(self, index: slice | int) -> str:
        """Allows retrieving bits of the Alphabet through [index] notation."""
        return self.alphabet[index]

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

    def __init__(self, key: str, alphabet: Alphabet | str | None = None):
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
        self._key: str = key
        self._key_length = len(self._key)

    @property
    def alphabet(self) -> Alphabet:
        """The Alphabet for this cipher."""
        return self._alphabet

    @property
    def key(self) -> str:
        """Shhh! This is the key. Keep it secret."""
        return self._key

    @property
    def modulus(self) -> int:
        """The modulus."""
        return self._alphabet.modulus

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
        output: list[Letter] = []

        """
        I would love to use zip and cycle, but I need to handle input
        characters that are not in the alphabet.
        """

        key_idx = 0
        for c in text:
            if c not in self.alphabet:
                result = c
            else:
                k = self.key[key_idx]
                result = operation(c, k)
                key_idx = (key_idx + 1) % self._key_length

            output.append(result)

        return "".join(output)

    def encrypt(self, plaintext: str) -> str:
        """Returns ciphertext."""

        return self.crypt(plaintext, mode="encrypt")

    def decrypt(self, ciphertext: str) -> str:
        """Returns plaintext."""

        return self.crypt(ciphertext, mode="decrypt")
