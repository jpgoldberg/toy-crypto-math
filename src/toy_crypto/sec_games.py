from collections.abc import Callable
import secrets
from typing import Generic, TypeVar

K = TypeVar("K")
"""Unbounded type variable intended for any type of key."""


class IndCpa(Generic[K]):
    def __init__(
        self,
        key_gen: Callable[[], K],
        encryptor: Callable[[K, bytes], bytes],
    ) -> None:
        """
        Meta setup for IND-CPA game.

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

    def new_challenger(
        self,
    ) -> Callable[[bytes, bytes], tuple[bytes, bool]]:
        """Creates a new challenger with random key."""

        key = self._key_gen()
        b = secrets.choice([True, False])

        def challenger(m0: bytes, m1: bytes) -> tuple[bytes, bool]:
            if len(m0) != len(m1):
                raise ValueError("Message lengths must be equal")

            m = m1 if b else m0

            encrypted = self._encryptor(key, m)
            return encrypted, b

        return challenger
