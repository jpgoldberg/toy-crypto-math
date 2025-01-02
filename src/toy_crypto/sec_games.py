from collections.abc import Callable, Mapping
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

        if self._key is None:
            raise Exception("game is not in a state where this can be called")

        if len(m0) != len(m1):
            raise ValueError("Message lengths must be equal")

        if self._b is None or self._key is None:
            raise Exception("Challenge is not be properly initialized")

        m = m1 if self._b else m0

        encrypted = self._encryptor(self._key, m)

        # prevent this from being called again with same key, b
        self._key = None

        return encrypted

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


_STATE_STARTED = "started"
_STATE_INITIALIZED = "initialized"
_STATE_ENCRYPTED = "encrypted_one"
_STATE_FINALIZED = "finalized"

# Next Allowed
_NA_INITIALIZE = "initialize"
_NA_ENCRYPT_ONE = "encrypt_one"
_NA_FINALIZE = "finalize"


class Ind(Generic[K]):
    def __init__(
        self,
        key_gen: Callable[[], K],
        encryptor: Callable[[K, bytes], bytes],
    ) -> None:
        """
        Class for some symmetric Indistinguishability games

        This is intended to be subclassed and not used directly.
        """

        self._key_gen = key_gen
        self._encryptor = encryptor

        self._key: Optional[K] = None
        self._b: Optional[bool] = None
        self._state = "started"

        # This is the IND-CPA mapping. IND-EAV will need a different state_map
        self._state_map: Mapping[str, list[str]] = {
            _STATE_STARTED: [_NA_INITIALIZE],
            _STATE_INITIALIZED: [_NA_ENCRYPT_ONE],
            _STATE_ENCRYPTED: [_NA_ENCRYPT_ONE, _NA_FINALIZE],
            _STATE_FINALIZED: [_NA_INITIALIZE],
        }

    def initialize(self) -> None:
        whoami = _NA_INITIALIZE
        if whoami not in self._state_map[self._state]:
            raise Exception(f"{whoami} not allowed in state {self._state}")
        """Challenger picks key and a b."""
        self._key = self._key_gen()
        self._b = secrets.choice([True, False])
        self._state = _STATE_INITIALIZED

    def encrypt_one(self, m0: bytes, m1: bytes) -> bytes:
        """Challenger encrypts m0 if b is False, else encrypts m1.

        :raise ValueError: if lengths of m0 and m1 are not equal.
        :raises Exception: if challenge isn't initialized.
        """

        whoami = _NA_ENCRYPT_ONE
        if whoami not in self._state_map[self._state]:
            raise Exception(f"{whoami} not allowed in state {self._state}")

        if len(m0) != len(m1):
            raise ValueError("Message lengths must be equal")

        if self._b is None or self._key is None:
            raise Exception("Challenge is not be properly initialized")

        m = m1 if self._b else m0

        self._state = _STATE_ENCRYPTED
        return self._encryptor(self._key, m)

    def finalize(self, guess: bool) -> bool:
        """
        True iff guess is the same as b of previously created challenger.

        Also resets the challenger, as for this game you cannot call with
        same key, b pair more than once.
        """

        whoami = _NA_FINALIZE
        if whoami not in self._state_map[self._state]:
            raise Exception(f"{whoami} not allowed in state {self._state}")
        adv_wins = guess == self._b

        self._state = _STATE_INITIALIZED

        return adv_wins


class IndCpa(Ind[K]):
    def __init__(
        self,
        key_gen: Callable[[], K],
        encryptor: Callable[[K, bytes], bytes],
    ) -> None:
        super().__init__(key_gen=key_gen, encryptor=encryptor)
        self._state_map = {
            _STATE_STARTED: [_NA_INITIALIZE],
            _STATE_INITIALIZED: [_NA_ENCRYPT_ONE],
            _STATE_ENCRYPTED: [_NA_ENCRYPT_ONE, _NA_FINALIZE],
            _STATE_FINALIZED: [_NA_INITIALIZE],
        }
