from collections.abc import Callable
import secrets
from typing import Generic, Optional, TypeVar

K = TypeVar("K")
"""Unbounded type variable intended for any type of key."""


class IndEav(Generic[K]):
    def __init__(
        self,
        key_gen: Callable[[], K],
        encryptor: Callable[[K, bytes], bytes],
    ) -> None:
        """
        IND-EAV game for symmetric encryption.

        Indistinguishability in presence of an eavesdropper.

        Takes an encryptor, which is a function that takes a key and bytes
        and outputs bytes. And takes a
        key generation function which
        produces a randomly chosen key appropriate for the encryptor.

        :param key_gen:
            A function that generates a random key for the encryption scheme.
        :param encryptor:
            A function that takes a key and bytes and outputs bytes.
        """

        self._key_gen = key_gen
        self._encryptor = encryptor
        self._recent_b: Optional[bool]

        self._key: Optional[K] = None
        self._b: Optional[bool] = None

    def initialize(self) -> None:
        """Challenger picks key and a b."""
        self._key = self._key_gen()
        self._b = secrets.choice([True, False])

    def encrypt_one(self, m0: bytes, m1: bytes) -> bytes:
        """Challenger encrypts m0 if b is False, else encrypts m1.

        :raise ValueError: if lengths of m0 and m1 are not equal.
        :raises Exception: if challenge isn't initialized.
        """

        if len(m0) != len(m1):
            raise ValueError("Message lengths must be equal")

        if self._b is None or self._key is None:
            raise Exception("Challenge is not be properly initialized")

        m = m1 if self._b else m0

        return self._encryptor(self._key, m)

    def finalize(self, guess: bool) -> bool:
        """
        True iff guess is the same as b of previously created challenger.

        Also resets the challenger, as for this game you cannot call with
        same key, b pair more than once.
        """

        adv_wins = guess == self._b

        self._b = None
        self._key = None

        return adv_wins
