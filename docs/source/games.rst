.. include:: ../common/unsafe.rst

*****************
Security games
*****************

.. py:module:: toy_crypto.sec_games
    :synopsis: Classes for running security games, including IND-CPA and IND-EAV.

    Imported with::

        import toy_crypto.sec_games

.. currentmodule:: toy_crypto.sec_games

The module includes a classes for running the several 
:wikipedia:`ciphertext indistisguishability <Ciphertext indistinguishability>` 
games for symmetric encryption game.

General Structure
==================

Indisitinguisibility games are set up as an adversary
playing against a game (or Challenger).
The game is given an encryption scheme and a key generation function.
So creating a game will often look like

.. code-block:: python

    def keygen() -> bytes:
        ...

    def encrypt(key: by, m: bytes) -> bytes:
        ...
    
    game = IndCpa(keygen, encrypt)

Once that is done, the adversary can interact with the game according to the rules of the particular game.

The first thing (in how I've coding things here) is that the adversary will tell the game to initialize itself.

.. code-block:: python

    game.initialize()
    ...
    
During that initialization the game will generate a key and randomly select 0 or 1 as the value of the bit **b**.
The adversary's task durig the course of the game is to figure out the value of **b**.
At the end of a round, the adversary will finalize the game by submitting its guess.

.. code-block:: python

    ...
    if game.finalize(guess):
        # Yay! Guessed correctly
        adv_score += 1

The only thing the adversary can do with the game after finalizing is
to tell it to re-initialize [#reinit]_ , which will generate a fresh key and value for the bit, **b**.

Between initialization and finalization the adversary can ask the game to
to perform certain computions, which may include encrypting or decrypting
data of the adversaries chosing. Which are available and in what sequences depends on the specific game.

The computation that is essential to all of these games is to encrypt one of 
two messages provided by the adversary.
The game returns a challenge ciphertext that is the encryption of one of
the messages depending on its value of **b**.
So the adversary is really trying to figure out if whether it is the left or right message that gets encrypted.

.. code-block:: python

    game.initialize()
    ...
    challenge_ctext = game.encrypt_one(m0, m1)
    ...
    if game.finalize(guess):
        ...

To save having to create many instances of a game with the same encryption 
scheme, py:func:`Ind.initialize` can be called after a game is
finalized to start over with a fresh key and **b**
while using the same encryption scheme. [#reinit]_


Examples
==========

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
============
.. autoclass:: StateError

Types for encryption scheme
============================

When a game is set up, it must be given an encryption scheme,
which will include a key generation function, an encryption function,
and optionally a decryption function.

Spinx doesn't seem to have good ways of documenting these,
but hopefully what I list here makes some sense.

.. autotypevar:: K

.. type:: KeyGenerator
    :canonical: Callable[[], K]

    A parameterized type alias for the key generation function.

.. type:: Cryptor
    :canonical: Callable[[K, bytes], bytes]

    A parameterized type alias to describe the encryptor/decrptor functions.


The class and method organization
==================================

All of the specific game classes are subclasses of the :class:`Ind` class.

.. autoclass:: Ind
    :class-doc-from: both
    :members: TRACK_CHALLENGE_CTEXTS

The classes optionally differ in which methods they offer and the sequence in which they are called.
That ordiering defined by the transition tables in :data:`T_TABLE`
with the initial stated being :data:`State.STARTED`.



All games allow the :func:`~Ind.initialize`,
:func:`~Ind.encrypt_one`
and :func:`~Ind.finalize`, methods.

.. automethod:: Ind.initialize

.. automethod:: Ind.encrypt_one

.. automethod:: Ind.finalize

Some of the games allow the :func:`~Ind.encrypt`
and :func:`~Ind.decrypt`, methods.

.. automethod:: Ind.encrypt

.. automethod:: Ind.decrypt


The only difference between :class:`IndEav` and :class:`IndCpa` is that the latter allows multiple calls to :func:`~IndCpa.encrypt_one`.

.. autoclass:: IndEav
    :class-doc-from: both

    .. autodata:: toy_crypto.sec_games.IndEav.T_TABLE
        :annotation:

    .. pprint:: toy_crypto.sec_games.IndEav.T_TABLE

    .. figure:: /images/IND-EAV.png
        :align: center
        :alt: State transition diagram generated from T_TABLE

        IND-EAV game states and transitions

    .. autoattribute:: toy_crypto.sec_games.IndEav.TRACK_CHALLENGE_CTEXTS

.. autoclass:: toy_crypto.sec_games.IndCpa
    :class-doc-from: both

    .. autodata:: toy_crypto.sec_games.IndCpa.T_TABLE
        :annotation:

    .. pprint:: toy_crypto.sec_games.IndCpa.T_TABLE
    

    .. figure:: /images/IND-CPA.png
        :align: center
        :alt: State transition diagram generated from T_TABLE

        IND-CPA game states and transitions

    .. autoattribute:: toy_crypto.sec_games.IndCpa.TRACK_CHALLENGE_CTEXTS

The only difference between :class:`IndCca1` and :class:`IndCca2` is 
the latter allows calls to :func:`~IndCca2.decrypt` the challenge ciphertext
has been provided by :func:`~IndCca2.encrypt_one`.
The challenge ciphertext cannot be given to :func:`~IndCca2.decrypt`.


.. autoclass:: toy_crypto.sec_games.IndCca1
    :class-doc-from: both

     .. autodata:: toy_crypto.sec_games.IndCca1.T_TABLE
        :annotation:

    .. pprint:: toy_crypto.sec_games.IndCca1.T_TABLE

    .. figure:: /images/IND-CCA1.png
        :align: center
        :alt: State transition diagram generated from T_TABLE

        IND-CCA1 game states and transitions

    .. autoattribute:: toy_crypto.sec_games.IndCca1.TRACK_CHALLENGE_CTEXTS

.. autoclass:: toy_crypto.sec_games.IndCca2
    :class-doc-from: both

    .. autodata:: toy_crypto.sec_games.IndCca2.T_TABLE
        :annotation:

    .. pprint:: toy_crypto.sec_games.IndCca2.T_TABLE

    .. figure:: /images/IND-CCA2.png
        :align: center
        :alt: State transition diagram generated from T_TABLE

        IND-CCA2 game states and transitions

    .. autoattribute:: toy_crypto.sec_games.IndCca2.TRACK_CHALLENGE_CTEXTS


State management tools
==============================

As described above, the difference between the particular gaves is defined
by what action the adversary can take when.
This is specified within the :class:`TransitionTable` for each.

.. autoenum:: State
    :members:

.. autoenum:: Action
    :members:

.. autoclass:: TransitionTable
    :class-doc-from: class
    :members: keys, __getitem__

.. autoprotocol:: SupportsTTable
    
    This protocol also depends on a private member. See source if you need to 
    make this work for something other than an :class:`Ind`.

Each method that the adversary can call is wrapped by the :deco:`manage_state` decorator

.. autodecorator:: manage_state


.. rubric:: Footnotes

.. [#reinit] The reason I separated game initialization from game creation is 
    because the user may wish to rerun a game many times.
    After all, the adversary doesn't need to win every time to win overall.
    It only needs to win meaningfully more than half the time.
    And so I didn't want to user to have to create a large number of
    instances of a game class and have to
    rely on the Python garbage collector to free up memory.

