.. include:: ../common/unsafe.rst

Security games
================================

This module is imported with::

    import toy_crypto.sec_games

.. currentmodule:: toy_crypto.sec_games

The module includes a class for running the IND-EAV
for symmetric encryption game. Perhaps more will be added later.


For testing, it is useful to have a challenge that the adversary can always
win, so we will use a shift ciper.
The adversary will set :code:`m0 = "AA"` and :code:`m1 = AB`.
If m0 is encrypted then the two bytes of the challenge ciphertext will
be the same as each other. If they differ, then m1 was encrypted.

.. testcode::
    
    import secrets
    from toy_crypto.sec_games import IndEav

    def encryptor(key: int, m: bytes) -> bytes:
        encrypted: bytes = bytes([(b + key) % 256 for b in m])
        return encrypted

    def key_gen() -> int:
        return secrets.randbelow(256)

    game = IndEav(key_gen, encryptor)
    game.initialize()

    m0 = b"AA"
    m1 = b"AB"
    ctext = game.encrypt_one(m0, m1)
    
    guess: bool = ctext[0] != ctext[1]

    assert game.finalize(guess)  # passes if guess is correct

        
The :mod:`~toy_crypto.sec_games` Module
----------------------------------------

.. automodule:: toy_crypto.sec_games
    :synopsis: Adversary / Challenger security games
    :members:
