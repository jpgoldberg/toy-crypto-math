from collections.abc import Callable, Mapping
import secrets
from typing import Generic, Optional, TypeVar
from toy_crypto.types import SupportsBool

K = TypeVar("K")
"""Unbounded type variable intended for any type of key."""

type KeyGenerator[K] = Callable[[], K]
"""To describe key generation functions"""

type Cryptor[K] = Callable[[K, bytes], bytes]
"""To describe encryptor/decryptor functions."""


class StateError(Exception):
    """When something attempted in an inappropriate state."""


_STATE_STARTED = "started"
_STATE_INITIALIZED = "initialized"
_STATE_ENCRYPTED = "encrypted_one"
_STATE_FINALIZED = "finalized"

# Next Allowed
_NA_START = "start"
_NA_INITIALIZE = "initialize"
_NA_ENCRYPT_ONE = "encrypt_one"
_NA_FINALIZE = "finalize"


class Ind(Generic[K]):
    def __init__(
        self,
        key_gen: KeyGenerator[K],
        encryptor: Cryptor[K],
        decryptor: Optional[Cryptor[K]] = None,
    ) -> None:
        """
        Class for some symmetric Indistinguishability games

        This is intended to be subclassed and not used directly.
        """

        self._key_gen = key_gen
        self._encryptor = encryptor

        self._key: Optional[K] = None
        self._b: Optional[bool] = None
        self._state = _STATE_STARTED

        """
        Each state is a dictionary of [Transition : State_Name]
        Transitions are the names of methods (or "start")
        """

        # This is the IND-CPA mapping. IND-EAV will need a different state_map
        self._state_map: Mapping[str, Mapping[str, str]] = {
            _STATE_STARTED: {_NA_INITIALIZE: _STATE_INITIALIZED},
            _STATE_INITIALIZED: {_NA_ENCRYPT_ONE: _STATE_ENCRYPTED},
            _STATE_ENCRYPTED: {
                _NA_ENCRYPT_ONE: _STATE_ENCRYPTED,
                _NA_FINALIZE: _STATE_STARTED,
            },
            _STATE_FINALIZED: {},
        }

    def _check_state(self, name: str) -> None:
        if name not in self._state_map[self._state]:
            raise StateError(f"{name} not allowed in state {self._state}")

    def _transition_state(self, name: str) -> None:
        self._state = self._state_map[self._state][name]

    def initialize(self) -> None:
        """Initializes self by creating key and selecting b."""
        whoami = _NA_INITIALIZE
        self._check_state(whoami)
        """Challenger picks key and a b."""
        self._key = self._key_gen()
        self._b = secrets.choice([True, False])
        self._transition_state(whoami)

    def encrypt_one(self, m0: bytes, m1: bytes) -> bytes:
        """Challenger encrypts m0 if b is False, else encrypts m1.

        :raise ValueError: if lengths of m0 and m1 are not equal.
        :raises Exception: if challenge isn't initialized.
        """

        whoami = _NA_ENCRYPT_ONE
        self._check_state(whoami)

        if self._b is None or self._key is None:
            raise Exception("Shouldn't happen in this state")

        if len(m0) != len(m1):
            raise ValueError("Message lengths must be equal")

        m = m1 if self._b else m0

        self._transition_state(whoami)
        return self._encryptor(self._key, m)

    def finalize(self, guess: SupportsBool) -> bool:
        """
        True iff guess is the same as b of previously created challenger.

        Also resets the challenger, as for this game you cannot call with
        same key, b pair more than once.
        """

        whoami = _NA_FINALIZE
        self._check_state(whoami)

        adv_wins = guess == self._b

        self._transition_state(whoami)

        return adv_wins


class IndCpa(Ind[K]):
    def __init__(
        self,
        key_gen: KeyGenerator[K],
        encryptor: Cryptor[K],
    ) -> None:
        """IND-CPA game.

        :param key_gen: A key generation function appropriate for encryptor
        :param encryptor:
            A function that that takes a key and message and outputs ctext
        :raises StateError: if methods called in disallowed order.
        """

        super().__init__(key_gen=key_gen, encryptor=encryptor)
        self._state_map: Mapping[str, Mapping[str, str]] = {
            _STATE_STARTED: {_NA_INITIALIZE: _STATE_INITIALIZED},
            _STATE_INITIALIZED: {_NA_ENCRYPT_ONE: _STATE_ENCRYPTED},
            _STATE_ENCRYPTED: {
                _NA_ENCRYPT_ONE: _STATE_ENCRYPTED,
                _NA_FINALIZE: _STATE_STARTED,
            },
            _STATE_FINALIZED: {},
        }


class IndEav(Ind[K]):
    def __init__(
        self,
        key_gen: KeyGenerator[K],
        encryptor: Cryptor[K],
    ) -> None:
        """IND-EAV game.

        :param key_gen: A key generation function appropriate for encryptor
        :param encryptor:
            A function that that takes a key and message and outputs ctext
        :raises StateError: if methods called in disallowed order.
        """

        super().__init__(key_gen=key_gen, encryptor=encryptor)
        self._state_map: Mapping[str, Mapping[str, str]] = {
            _STATE_STARTED: {_NA_INITIALIZE: _STATE_INITIALIZED},
            _STATE_INITIALIZED: {_NA_ENCRYPT_ONE: _STATE_ENCRYPTED},
            _STATE_ENCRYPTED: {
                _NA_FINALIZE: _STATE_STARTED,
            },
            _STATE_FINALIZED: {},
        }
