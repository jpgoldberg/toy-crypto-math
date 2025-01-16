from collections.abc import Callable, Mapping
from enum import StrEnum
import secrets
from typing import Generic, Optional, TypeVar
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


class State(StrEnum):
    """The state a game."""

    STARTED = "S"
    """Game has not been initialized."""

    INITIALIZED = "I"
    """Game is initialized"""

    CHALLENGED = "C"
    """Challenge text created."""


class Action(StrEnum):
    """Adversary actions (Methods called by A)."""

    INITIALIZE = "initialize"
    """initialize() called."""

    ENCRYPT_ONE = "encrypt_one"
    """encrypt_one() called."""

    ENCRYPT = "encrypt"
    """encrypt() called."""

    DECRYPT = "decrypt"
    """decrypt() called"""

    FINALIZE = "finalize"
    """finalize() called."""


type TransitionTable = Mapping[State, Mapping[Action, State]]
"""Transition Table to manage state of a game."""


class Ind(Generic[K]):
    T_TABLE: Mapping[State, Mapping[Action, State]]

    def __init__(
        self,
        key_gen: KeyGenerator[K],
        encryptor: Cryptor[K],
        decryptor: Optional[Cryptor[K]] = None,
        transition_table: Optional[TransitionTable] = None,
    ) -> None:
        """
        A super class for symmetric Indistinguishability games.

        Unless the user provides an appropriate transition table,
        no methods will be allowed.
        """

        self._key_gen = key_gen
        self._encryptor = encryptor
        self._decryptor = decryptor if decryptor else self._undefined_decryptor

        self._key: Optional[K] = None
        self._b: Optional[bool] = None
        self._state = State.STARTED

        # Only needed for CCA2, but having it here makes
        # initialization method more general.
        self._challenge_ctexts: set[str] = set()

        """
        Each state is a dictionary of [Transition : State_Name]
        Transitions are the names of methods (or "start")
        """

        self._t_table: TransitionTable = {}
        if transition_table:
            self._t_table = transition_table

    def _handle_state(self, name: Action) -> None:
        if name not in self._t_table[self._state]:
            raise StateError(f"{name} not allowed in state {self._state}")
        self._state = (self._t_table[self._state])[name]

    def _undefined_decryptor(self, key: K, ctext: bytes) -> bytes:
        raise StateError("Method not allowed in this game")
        return (  # Compiler should know this is unreachable
            b"Does this ever return?"
            b" No, this never returns,"
            b" And its fate is still unlearned.",
        )

    def initialize(self) -> None:
        """Initializes self by creating key and selecting b.

        :raises StateError: if method called when disallowed.
        """
        whoami = Action.INITIALIZE
        self._handle_state(whoami)
        """Challenger picks key and a b."""
        self._key = self._key_gen()
        self._b = secrets.choice([True, False])
        self._challenge_ctexts = set()

    def encrypt_one(self, m0: bytes, m1: bytes) -> bytes:
        """Left-Right encryption oracle.

        Challenger encrypts m0 if b is False, else encrypts m1.

        :param m0: Left message
        :param m1: Right message
        :raise ValueError: if lengths of m0 and m1 are not equal.
        :raises StateError: if method called when disallowed.
        """

        whoami = Action.ENCRYPT_ONE
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
        whoami = Action.ENCRYPT
        self._handle_state(whoami)

        if self._key is None:
            raise StateError("key should exist in this state")

        return self._encryptor(self._key, ptext)

    def decrypt(self, ctext: bytes) -> bytes:
        """Decryption oracle.

        :param ctext: Ciphertext to be decrypted
        :raises StateError: if method called when disallowed.
        """
        whoami = Action.DECRYPT
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

        whoami = Action.FINALIZE
        self._handle_state(whoami)

        adv_wins = guess == self._b

        return adv_wins


class IndCpa(Ind[K]):
    T_TABLE: TransitionTable = {
        State.STARTED: {Action.INITIALIZE: State.INITIALIZED},
        State.INITIALIZED: {Action.ENCRYPT_ONE: State.CHALLENGED},
        State.CHALLENGED: {
            Action.ENCRYPT_ONE: State.CHALLENGED,
            Action.FINALIZE: State.STARTED,
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
    T_TABLE: TransitionTable = {
        State.STARTED: {Action.INITIALIZE: State.INITIALIZED},
        State.INITIALIZED: {Action.ENCRYPT_ONE: State.CHALLENGED},
        State.CHALLENGED: {
            Action.FINALIZE: State.STARTED,
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
    T_TABLE: TransitionTable = {
        State.STARTED: {Action.INITIALIZE: State.INITIALIZED},
        State.INITIALIZED: {
            Action.ENCRYPT_ONE: State.CHALLENGED,
            Action.ENCRYPT: State.INITIALIZED,
            Action.DECRYPT: State.INITIALIZED,
        },
        State.CHALLENGED: {
            Action.FINALIZE: State.STARTED,
            Action.ENCRYPT: State.CHALLENGED,
            Action.DECRYPT: State.CHALLENGED,
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
    T_TABLE: TransitionTable = {
        State.STARTED: {Action.INITIALIZE: State.INITIALIZED},
        State.INITIALIZED: {
            Action.ENCRYPT_ONE: State.CHALLENGED,
            Action.ENCRYPT: State.INITIALIZED,
            Action.DECRYPT: State.INITIALIZED,
        },
        State.CHALLENGED: {
            Action.FINALIZE: State.STARTED,
            Action.ENCRYPT: State.CHALLENGED,
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

    def encrypt_one(self, m0: bytes, m1: bytes) -> bytes:
        ctext = super().encrypt_one(m0, m1)
        self._challenge_ctexts.add(hash_bytes(ctext))
        return ctext
