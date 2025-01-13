.. include:: ../common/unsafe.rst

Security games
================================

.. py:module:: toy_crypto.sec_games
    :synopsis: Classes for running security games, including IND-CPA and IND-EAV.

    Imported with::

        import toy_crypto.sec_games

.. currentmodule:: toy_crypto.sec_games

The module includes a classes for running the several 
ciphertext indistisguishability games for symmetric encryption game.

Examples
---------

For testing, it is useful to have a challenge that the adversary can always
win, so we will use a shift ciper for testing IND-EAV
and a reused pad (N-time-pad) for testing IND-CPA.

.. testcode::
    
    import secrets
    from toy_crypto.sec_games import IndEav, IndCpa

    def shift_encrypt(key: int, m: bytes) -> bytes:
        encrypted: bytes = bytes([(b + key) % 256 for b in m])
        return encrypted

    def shift_keygen() -> int:
        return secrets.randbelow(256)


The shift-cipher IND-EAV condition
(and thus does not provide semantic security).
The adversary will set :code:`m0 = "AA"` and :code:`m1 = AB`.
If m0 is encrypted then the two bytes of the challenge ciphertext will
be the same as each other. If they differ, then m1 was encrypted.

.. testcode::
    
    game = IndEav(shift_keygen, shift_encrypt)
    game.initialize()

    m0 = b"AA"
    m1 = b"AB"
    ctext = game.encrypt_one(m0, m1)
    
    guess: bool = ctext[0] != ctext[1]

    assert game.finalize(guess)  # passes if guess is correct

Let's use a stronger cipher, the N-Time-Pad for our IND-CPA example.

.. testcode::

    # import secrets  # already imported
    from toy_crypto.utils import xor

    def ntp_keygen() -> bytes:
        return secrets.token_bytes(16)

    def ntp_encrypt(key: bytes, m: bytes) -> bytes:
        if len(m) > len(key):
            raise ValueError("message too long")
        return xor(key, m)

The N-Time-Pad (up to limited message length) is semantically secure.
One can prove that any adversary that can reliability win the IND-EAV game
can reliabily predict bits from the presumed security random number generator.
Thus the NTP is at least as secure as the random number generator.

But because the NTP is deterministic it will fail IND-CPA security.

.. testcode::

    game = IndCpa(ntp_keygen, ntp_encrypt)
    game.initialize()

    m0 = b"Attack at dawn!"
    m1 = b"Attack at dusk!"
    ctext1 = game.encrypt_one(m0, m1)
    ctext2 = game.encrypt_one(m1, m1)
    
    guess: bool = ctext1 == ctext2

    assert game.finalize(guess)  # passes if guess is correct


Exceptions
-----------
.. autoclass:: StateError

Type aliases and parameters
----------------------------

Our classes have some nastly looking type parameters,
so we define some type aliases to make things easier.

.. autoclass:: K

.. py:data:: KeyGenerator

    A parameterized type alias to describe the key generator functions.
    defined as :code:`Callable[[], K]`

.. py:data:: Cryptor

    A parameterized type alias to describe the encryptor/decrptor functions.
    defined as :code:`Callable[[K, bytes], bytes]`

The :mod:`~toy_crypto.sec_games` Classes
----------------------------------------

The classes only differ by the order in which methods can be called.
And that ordiering defined by the transition tables in :data:`T_TABLE`
with the initial stated being "started".

.. autoclass:: IndEav
    :class-doc-from: both
    :members: T_TABLE, initialize, encrypt_one, finalize

.. autoclass:: toy_crypto.sec_games.IndCpa
    :class-doc-from: both
    :members: T_TABLE, initialize, encrypt_one, finalize

.. autoclass:: toy_crypto.sec_games.IndCca1
    :class-doc-from: both
    :members: T_TABLE, initialize, encrypt, decrypt, encrypt_one, finalize

.. autoclass:: toy_crypto.sec_games.IndCca2
    :class-doc-from: both
    :members: T_TABLE, initialize, encrypt, decrypt, encrypt_one, finalize

