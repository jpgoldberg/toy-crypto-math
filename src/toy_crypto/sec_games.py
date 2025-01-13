from collections.abc import Callable, Mapping
import secrets
from typing import Any, Generic, Optional, TypeVar
from toy_crypto.types import SupportsBool
from toy_crypto.utils import hash_bytes

K = TypeVar("K")
"""Unbounded type variable intended for any type of key."""

type KeyGenerator[K] = Callable[[], K]
"""To describe key generation functions"""

type Cryptor[K] = Callable[[K, bytes], bytes]
"""To describe encryptor/decryptor functions."""


class StateError(Exception):
    """When something attempted in an inappropriate state."""


_STATE_STARTED = "UN-INITIALIZED"
_STATE_INITIALIZED = "INITIALIZED"
_STATE_CHALLANGE_CREATED = "CHALLENGE-CREATED"

# Adversary Action
_AA_INITIALIZE = "initialize"
_AA_ENCRYPT_ONE = "encrypt_one"
_AA_ENCRYPT = "encrypt"
_AA_DECRYPT = "decrypt"
_AA_FINALIZE = "finalize"


class Ind(Generic[K]):
    def __init__(
        self,
        key_gen: KeyGenerator[K],
        encryptor: Cryptor[K],
        decryptor: Optional[Cryptor[K]] = None,
        transition_table: Optional[Mapping[str, Mapping[str, str]]] = None,
    ) -> None:
        """
        Class for some symmetric Indistinguishability games

        This is intended to be subclassed and not used directly.
        """

        self._key_gen = key_gen
        self._encryptor = encryptor
        self._decryptor = decryptor if decryptor else self._disallowed_method

        self._key: Optional[K] = None
        self._b: Optional[bool] = None
        self._state = _STATE_STARTED

        """
        Each state is a dictionary of [Transition : State_Name]
        Transitions are the names of methods (or "start")
        """

        self._t_table: Mapping[str, Mapping[str, str]] = {}
        if transition_table:
            self._t_table = transition_table

    def _handle_state(self, name: str) -> None:
        if name not in self._t_table[self._state]:
            raise StateError(f"{name} not allowed in state {self._state}")
        self._state = self._t_table[self._state][name]

    def _disallowed_method(self, *args: Any, **kwargs: Any) -> Any:
        raise StateError("Method not allowed in this game")

    def initialize(self) -> None:
        """Initializes self by creating key and selecting b.

        :raises StateError: if method called when disallowed.
        """
        whoami = _AA_INITIALIZE
        self._handle_state(whoami)
        """Challenger picks key and a b."""
        self._key = self._key_gen()
        self._b = secrets.choice([True, False])

    def encrypt_one(self, m0: bytes, m1: bytes) -> bytes:
        """Left-Right encryption oracle.

        Challenger encrypts m0 if b is False, else encrypts m1.

        :param m0: Left message
        :param m1: Right message
        :raise ValueError: if lengths of m0 and m1 are not equal.
        :raises StateError: if method called when disallowed.
        """

        whoami = _AA_ENCRYPT_ONE
        self._handle_state(whoami)

        if self._b is None or self._key is None:
            raise StateError("key should exist in this state")

        if len(m0) != len(m1):
            raise ValueError("Message lengths must be equal")

        m = m1 if self._b else m0

        return self._encryptor(self._key, m)

    def encrypt(self, ptext: bytes) -> bytes:
        """Encryption oracle.

        :param ptext: Message to be encrypted
        :raises StateError: if method called when disallowed.
        """
        whoami = _AA_ENCRYPT
        self._handle_state(whoami)

        if self._key is None:
            raise StateError("key should exist in this state")

        return self._encryptor(self._key, ptext)

    def decrypt(self, ctext: bytes) -> bytes:
        """Decryption oracle.

        :param ctext: Ciphertext to be decrypted
        :raises StateError: if method called when disallowed.
        """
        whoami = _AA_DECRYPT
        self._handle_state(whoami)

        if self._key is None:
            raise StateError("key should exist in this state")

        return self._decryptor(self._key, ctext)

    def finalize(self, guess: SupportsBool) -> bool:
        """
        True iff guess is the same as b of previously created challenger.

        Also resets the challenger, as for this game you cannot call with
        same key, b pair more than once.

        :raises StateError: if method called when disallowed.
        """

        whoami = _AA_FINALIZE
        self._handle_state(whoami)

        adv_wins = guess == self._b

        return adv_wins


class IndCpa(Ind[K]):
    T_TABLE: Mapping[str, Mapping[str, str]] = {
        _STATE_STARTED: {_AA_INITIALIZE: _STATE_INITIALIZED},
        _STATE_INITIALIZED: {_AA_ENCRYPT_ONE: _STATE_CHALLANGE_CREATED},
        _STATE_CHALLANGE_CREATED: {
            _AA_ENCRYPT_ONE: _STATE_CHALLANGE_CREATED,
            _AA_FINALIZE: _STATE_STARTED,
        },
    }
    """Transition table for CPA game."""

    def __init__(
        self,
        key_gen: KeyGenerator[K],
        encryptor: Cryptor[K],
    ) -> None:
        """IND-CPA game.

        :param key_gen: A key generation function appropriate for encryptor
        :param encryptor:
            A function that takes a key and message and outputs ctext
        """

        super().__init__(key_gen=key_gen, encryptor=encryptor)
        self._t_table = self.T_TABLE


class IndEav(Ind[K]):
    T_TABLE: Mapping[str, Mapping[str, str]] = {
        _STATE_STARTED: {_AA_INITIALIZE: _STATE_INITIALIZED},
        _STATE_INITIALIZED: {_AA_ENCRYPT_ONE: _STATE_CHALLANGE_CREATED},
        _STATE_CHALLANGE_CREATED: {
            _AA_FINALIZE: _STATE_STARTED,
        },
    }
    """Transition table for EAV game"""

    def __init__(
        self,
        key_gen: KeyGenerator[K],
        encryptor: Cryptor[K],
    ) -> None:
        """IND-EAV game.

        :param key_gen: A key generation function appropriate for encryptor
        :param encryptor:
            A function that takes a key and message and outputs ctext
        :raises StateError: if methods called in disallowed order.
        """

        super().__init__(key_gen=key_gen, encryptor=encryptor)
        self._t_table = self.T_TABLE


class IndCca2(Ind[K]):
    T_TABLE: Mapping[str, Mapping[str, str]] = {
        _STATE_STARTED: {_AA_INITIALIZE: _STATE_INITIALIZED},
        _STATE_INITIALIZED: {
            _AA_ENCRYPT_ONE: _STATE_CHALLANGE_CREATED,
            _AA_ENCRYPT: _STATE_INITIALIZED,
            _AA_DECRYPT: _STATE_INITIALIZED,
        },
        _STATE_CHALLANGE_CREATED: {
            _AA_FINALIZE: _STATE_STARTED,
            _AA_ENCRYPT: _STATE_CHALLANGE_CREATED,
            _AA_DECRYPT: _STATE_CHALLANGE_CREATED,
        },
    }
    """Transition table for IND-CCA2 game"""

    def __init__(
        self,
        key_gen: KeyGenerator[K],
        encryptor: Cryptor[K],
        decrytpor: Cryptor[K],
    ) -> None:
        """IND-CCA game.

        :param key_gen: A key generation function appropriate for encryptor
        :param encryptor:
            A function that takes a key and message and outputs ctext
        :param decryptor:
            A function that takes a key and ciphertext and outputs plaintext
        :raises StateError: if methods called in disallowed order.
        """

        super().__init__(
            key_gen=key_gen, encryptor=encryptor, decryptor=decrytpor
        )
        self._t_table = self.T_TABLE

        """
        We will need to keep track of the challenge ctext created by
        encrypt_one to prevent any decryption of it.
        """

        self._challenge_ctexts: set[str] = set()

    def encrypt_one(self, m0: bytes, m1: bytes) -> bytes:
        ctext = super().encrypt_one(m0, m1)
        self._challenge_ctexts.add(hash_bytes(ctext))
        return ctext

    def decrypt(self, ctext: bytes) -> bytes:
        if hash_bytes(ctext) in self._challenge_ctexts:
            raise Exception(
                "Adversary is not allowed to call decrypt on challenge ctext"
            )
        return super().decrypt(ctext)


class IndCca1(Ind[K]):
    T_TABLE: Mapping[str, Mapping[str, str]] = {
        _STATE_STARTED: {_AA_INITIALIZE: _STATE_INITIALIZED},
        _STATE_INITIALIZED: {
            _AA_ENCRYPT_ONE: _STATE_CHALLANGE_CREATED,
            _AA_ENCRYPT: _STATE_INITIALIZED,
            _AA_DECRYPT: _STATE_INITIALIZED,
        },
        _STATE_CHALLANGE_CREATED: {
            _AA_FINALIZE: _STATE_STARTED,
            _AA_ENCRYPT: _STATE_CHALLANGE_CREATED,
        },
    }
    """Transition table for IND-CCA1 game"""

    def __init__(
        self,
        key_gen: KeyGenerator[K],
        encryptor: Cryptor[K],
        decrytpor: Cryptor[K],
    ) -> None:
        """IND-CCA game.

        :param key_gen: A key generation function appropriate for encryptor
        :param encryptor:
            A function that takes a key and message and outputs ctext
        :param decryptor:
            A function that takes a key and ciphertext and outputs plaintext
        :raises StateError: if methods called in disallowed order.
        """

        super().__init__(
            key_gen=key_gen, encryptor=encryptor, decryptor=decrytpor
        )
        self._t_table = self.T_TABLE

        """
        We will need to keep track of the challenge ctext created by
        encrypt_one to prevent any decryption of it.
        """

        self._challenge_ctexts: set[str] = set()

    def encrypt_one(self, m0: bytes, m1: bytes) -> bytes:
        ctext = super().encrypt_one(m0, m1)
        self._challenge_ctexts.add(hash_bytes(ctext))
        return ctext
