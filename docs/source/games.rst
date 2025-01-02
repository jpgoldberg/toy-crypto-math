.. include:: ../common/unsafe.rst

Security games
================================

This module is imported with::

    import toy_crypto.sec_games

.. currentmodule:: toy_crypto.sec_games

The module includes a classes for running the IND-CPA and IND-EAV
games for symmetric encryption game. Perhaps more will be added later.

Examples
---------

For testing, it is useful to have a challenge that the adversary can always
win, so we will use a shift ciper.

.. testcode::
    
    import secrets
    from toy_crypto.sec_games import IndEav, IndCpa

    def encryptor(key: int, m: bytes) -> bytes:
        encrypted: bytes = bytes([(b + key) % 256 for b in m])
        return encrypted

    def key_gen() -> int:
        return secrets.randbelow(256)

As a shift-cipher is deterministic, the Adversary can always win the CPA game.

.. testcode::

    game = IndCpa(key_gen, encryptor)
    game.initialize()

    m0 = b"Attack at dawn!"
    m1 = b"Attack at dusk!"
    ctext1 = game.encrypt_one(m0, m1)
    ctext2 = game.encrypt_one(m1, m1)
    
    guess: bool = ctext1 == ctext2

    assert game.finalize(guess)  # passes if guess is correct

The shift-cipher fails the even weaker IND-EAV condition
(and thus does not provide semantic security).
The adversary will set :code:`m0 = "AA"` and :code:`m1 = AB`.
If m0 is encrypted then the two bytes of the challenge ciphertext will
be the same as each other. If they differ, then m1 was encrypted.

.. testcode::
    
    game = IndEav(key_gen, encryptor)
    game.initialize()

    m0 = b"AA"
    m1 = b"AB"
    ctext = game.encrypt_one(m0, m1)
    
    guess: bool = ctext[0] != ctext[1]

    assert game.finalize(guess)  # passes if guess is correct


Exceptions
-----------
.. autoclass:: StateError

Types 
------------

Our classes have some nastly looking type parameters,
so we define some type aliases to make things easier.

As I can't seem to get automatic documenation of these,
here is the code that defines the the types.

.. code-block:: python

    K = TypeVar("K")
    """Unbounded type variable intended for any type of key."""

    type KeyGenerator[K] = Callable[[], K]
    """To describe key generation functions"""

    type Encryptor[K] = Callable[[K, bytes], bytes]
    """To describe encryptor functions."""


The :mod:`~toy_crypto.sec_games` Classes
----------------------------------------

.. autoclass:: IndEav
    :class-doc-from: both
    :inherited-members:

.. autoclass:: toy_crypto.sec_games.IndCpa
    :class-doc-from: both
    :inherited-members:
