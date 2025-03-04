from collections.abc import Callable, KeysView, Mapping
from dataclasses import dataclass
from enum import StrEnum
import secrets
from typing import Any, Generic, Optional, TypeVar, cast, Protocol
from functools import wraps
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
    """Adversary actions (Methods called)."""

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


@dataclass
class TransitionTable:
    """Transition Table to manage state of a game.

    It can be treated like a mapping.
    """

    table: Mapping[State, Mapping[Action, State]]

    def keys(self) -> KeysView[State]:
        """Just like ``keys`` for a real dict."""
        return self.table.keys()

    def __getitem__(self, item: State) -> Mapping[Action, State]:
        """So that items can be looked up with ``[key]`` as in a real dict."""
        return self.table[item]

    def __str__(self) -> str:
        pad = "  "
        if len(self.table) == 0:
            return "{ }"
        result = "{\n"
        for key in self.keys():
            result += f"{pad}State.{key.name}:\n"
            for act in self.table[key].keys():
                result += f"{pad * 2}Action.{act.name}"
                result += f" -> State.{self.table[key][act].name}\n"
        result += "}"
        return result


class SupportsTTable(Protocol):
    """Has what it takes to be decorated by :func:`manage_state`."""

    t_table: TransitionTable
    current_state: State
    _state: State


# This lexical scoping trickery is based on
#    https://stackoverflow.com/a/38286176/1304076
# with a hat tip to https://www.reddit.com/user/GeorgeFranklyMathnet/
#  https://www.reddit.com/r/learnpython/comments/1i34vgh/comment/m7k6hgn/
def manage_state[F: Callable[..., Any]](fn: F) -> F:
    """Decorator to check/transition state for Ind method calls."""
    action = Action(fn.__name__)

    @wraps(fn)
    def decorator(self: SupportsTTable, *args, **kwargs):  # type: ignore
        if action not in self.t_table[self.current_state]:
            raise StateError(
                f"{action} not allowed in state {self.current_state}"
            )
        retvalue = fn(self, *args, **kwargs)
        self._state = (self.t_table[self._state])[action]
        return retvalue

    return cast(F, decorator)


class Ind(Generic[K]):
    T_TABLE: TransitionTable

    #: Game does not track which challenge texts have been created
    TRACK_CHALLENGE_CTEXTS: bool

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

        self._challenge_ctexts: set[str] = set()

        """
        Each state is a dictionary of [Transition : State_Name]
        Transitions are the names of methods (or "start")
        """

        self._t_table = TransitionTable({})
        if transition_table:
            self._t_table = transition_table

    @property
    def t_table(self) -> TransitionTable:
        return self._t_table

    @property
    def current_state(self) -> State:
        return self._state

    def _undefined_decryptor(self, key: K, ctext: bytes) -> bytes:
        raise StateError("Method not allowed in this game")
        return (  # Compiler should know this is unreachable
            b"Does this ever return?"
            b" No, this never returns,"
            b" And its fate is still unlearned.",
        )

    @manage_state
    def initialize(self) -> None:
        """Initializes self by creating key and selecting b.

        Also clears an saved challenge ciphertexts.

        :raises StateError: if method called when disallowed.
        """

        """Challenger picks key and a b."""
        self._key = self._key_gen()
        self._b = secrets.choice([True, False])
        self._challenge_ctexts = set()

    @manage_state
    def encrypt_one(self, m0: bytes, m1: bytes) -> bytes:
        """Left-Right encryption oracle.

        Challenger encrypts m0 if b is False, else encrypts m1.

        :param m0: Left message
        :param m1: Right message
        :raise ValueError: if lengths of m0 and m1 are not equal.
        :raises StateError: if method called when disallowed.
        """

        # If these are None at this point, you've got a bad TransitionTable.
        cast(bool, self._b)
        cast(K, self._key)

        # Hmm, casts aren't working for me.
        assert self._key is not None

        if len(m0) != len(m1):
            raise ValueError("Message lengths must be equal")

        m = m1 if self._b else m0

        ctext = self._encryptor(self._key, m)
        if self.TRACK_CHALLENGE_CTEXTS:
            self._challenge_ctexts.add(hash_bytes(ctext))
        return ctext

    @manage_state
    def encrypt(self, ptext: bytes) -> bytes:
        """Encryption oracle.

        :param ptext: Message to be encrypted
        :raises StateError: if method called when disallowed.
        """

        assert self._key is not None
        return self._encryptor(self._key, ptext)

    @manage_state
    def decrypt(self, ctext: bytes) -> bytes:
        """Decryption oracle.

        :param ctext: Ciphertext to be decrypted
        :raises StateError: if method called when disallowed.
        """

        assert self._key is not None

        if hash_bytes(ctext) in self._challenge_ctexts:
            raise Exception(
                "Adversary is not allowed to call decrypt on challenge ctext"
            )

        return self._decryptor(self._key, ctext)

    @manage_state
    def finalize(self, guess: SupportsBool) -> bool:
        """
        True iff guess is the same as b of previously created challenger.

        :raises StateError: if method called when disallowed.
        """

        return guess == self._b


class IndCpa(Ind[K]):
    T_TABLE = TransitionTable(
        {
            State.STARTED: {Action.INITIALIZE: State.INITIALIZED},
            State.INITIALIZED: {Action.ENCRYPT_ONE: State.CHALLENGED},
            State.CHALLENGED: {
                Action.ENCRYPT_ONE: State.CHALLENGED,
                Action.FINALIZE: State.STARTED,
            },
        }
    )
    """Transition table for CPA game."""

    TRACK_CHALLENGE_CTEXTS = False
    """This game does not need to record challenge ctexts."""

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
    T_TABLE = TransitionTable(
        {
            State.STARTED: {Action.INITIALIZE: State.INITIALIZED},
            State.INITIALIZED: {Action.ENCRYPT_ONE: State.CHALLENGED},
            State.CHALLENGED: {
                Action.FINALIZE: State.STARTED,
            },
        }
    )
    """Transition table for EAV game"""

    TRACK_CHALLENGE_CTEXTS = False
    """This game does not need to record challenge ctexts."""

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
    T_TABLE = TransitionTable(
        {
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
    )
    """Transition table for IND-CCA2 game"""

    TRACK_CHALLENGE_CTEXTS = True
    """CCA2 needs to prevent decrypt() from decrypting challenge ctexts."""

    def __init__(
        self,
        key_gen: KeyGenerator[K],
        encryptor: Cryptor[K],
        decrytpor: Cryptor[K],
    ) -> None:
        """IND-CCA2 game.

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


class IndCca1(Ind[K]):
    T_TABLE = TransitionTable(
        {
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
    )
    """Transition table for IND-CCA1 game"""

    TRACK_CHALLENGE_CTEXTS = False
    """This game does not need to record challenge ctexts."""

    def __init__(
        self,
        key_gen: KeyGenerator[K],
        encryptor: Cryptor[K],
        decrytpor: Cryptor[K],
    ) -> None:
        """IND-CCA1 game.

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
